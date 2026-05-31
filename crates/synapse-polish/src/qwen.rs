//! Qwen-Flash (and any OpenAI-compatible chat completions endpoint) Polish provider.
//!
//! ## Why OpenAI-compatible
//!
//! Both Aliyun's bailian / DashScope (`qwen-flash`, `qwen-turbo` etc.) and
//! Volc Engine's ARK chat completions speak the OpenAI-compatible Chat
//! Completions schema. Same goes for self-hosted vLLM / Ollama / LM Studio
//! deployments. One adapter covers all of them — only the endpoint URL and
//! model id change.
//!
//! ## Budget contract
//!
//! `PolishProvider::polish` must respect the caller's `budget`. We send
//! the request with `tokio::time::timeout`. If the budget is exceeded,
//! we return `PolishError::BudgetExceeded` and the caller (the daemon's
//! `drive` task) falls back to the raw ASR result. Polish is best-effort
//! — it must never block the user from seeing their text.

use std::time::Duration;

use async_trait::async_trait;
use serde::{Deserialize, Serialize};

use crate::audit::{audit, AuditResult, RejectReason};
use crate::{PolishError, PolishProvider, PolishRequest};

#[derive(Debug, Clone)]
pub struct QwenConfig {
    /// Full chat-completions URL, e.g.
    /// `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`
    /// or `https://ark.cn-beijing.volces.com/api/v3/chat/completions`.
    pub endpoint: String,
    /// API key for Bearer auth.
    pub api_key: String,
    /// Model id, e.g. `qwen-flash` or `doubao-pro-4k`.
    pub model: String,
    /// Optional override for the system prompt. Defaults to the built-in
    /// strict-no-hallucination prompt.
    pub system_prompt: Option<String>,
    /// Optional name override for telemetry. Defaults to `"qwen"`.
    pub display_name: Option<&'static str>,
}

impl QwenConfig {
    pub fn new(
        endpoint: impl Into<String>,
        api_key: impl Into<String>,
        model: impl Into<String>,
    ) -> Self {
        Self {
            endpoint: endpoint.into(),
            api_key: api_key.into(),
            model: model.into(),
            system_prompt: None,
            display_name: None,
        }
    }
}

#[derive(Debug, Clone)]
pub struct QwenPolishProvider {
    cfg: QwenConfig,
    http: reqwest::Client,
}

impl QwenPolishProvider {
    pub fn new(cfg: QwenConfig) -> Self {
        let http = reqwest::Client::builder()
            // Connect timeout is separate from per-request budget, used to
            // fail fast on dead endpoints.
            .connect_timeout(Duration::from_millis(300))
            .build()
            .expect("reqwest::Client::build with default rustls is infallible");
        Self { cfg, http }
    }
}

const DEFAULT_SYSTEM_PROMPT: &str = r#"你是一个中英文混合输入的修正器。修正下面的 ASR 结果中的错别字、专业术语、标点。

严格遵守：
1. 不得增加任何原文没有的语义信息。
2. 不得删除任何原文有的语义信息。
3. 中英文之间保持一个空格。
4. 直接输出修正后的文本，不要任何解释、不要 Markdown 代码块、不要引号包裹。

如果原文已经正确，直接原样返回。"#;

#[derive(Debug, Serialize)]
struct ChatRequest<'a> {
    model: &'a str,
    messages: Vec<ChatMessage<'a>>,
    temperature: f32,
    /// Cap the response so the LLM can't run away if it ignores instructions.
    max_tokens: u32,
    stream: bool,
}

#[derive(Debug, Serialize)]
struct ChatMessage<'a> {
    role: &'a str,
    content: String,
}

#[derive(Debug, Deserialize)]
struct ChatResponse {
    choices: Vec<ChatChoice>,
}

#[derive(Debug, Deserialize)]
struct ChatChoice {
    message: ChatChoiceMessage,
}

#[derive(Debug, Deserialize)]
struct ChatChoiceMessage {
    content: String,
}

#[async_trait]
impl PolishProvider for QwenPolishProvider {
    fn name(&self) -> &'static str {
        self.cfg.display_name.unwrap_or("qwen")
    }

    async fn polish(&self, req: PolishRequest, budget: Duration) -> Result<String, PolishError> {
        if req.raw.trim().is_empty() {
            return Ok(req.raw);
        }

        let user_content = build_user_message(&req);
        let system_prompt: &str = self
            .cfg
            .system_prompt
            .as_deref()
            .unwrap_or(DEFAULT_SYSTEM_PROMPT);

        let body = ChatRequest {
            model: &self.cfg.model,
            messages: vec![
                ChatMessage {
                    role: "system",
                    content: system_prompt.to_string(),
                },
                ChatMessage {
                    role: "user",
                    content: user_content,
                },
            ],
            temperature: 0.0,
            // Cap at ~2x the input character count, never below 64.
            max_tokens: ((req.raw.chars().count() * 2).max(64)) as u32,
            stream: false,
        };

        let polished = tokio::time::timeout(budget, self.call(body))
            .await
            .map_err(|_| PolishError::BudgetExceeded(budget))??;

        let polished = strip_wrapping(&polished);
        match audit(&req.raw, &polished) {
            AuditResult::Accept => Ok(polished),
            AuditResult::Reject(reason) => Err(PolishError::Rejected(format_reject(reason))),
        }
    }
}

impl QwenPolishProvider {
    async fn call(&self, body: ChatRequest<'_>) -> Result<String, PolishError> {
        let resp = self
            .http
            .post(&self.cfg.endpoint)
            .bearer_auth(&self.cfg.api_key)
            .json(&body)
            .send()
            .await
            .map_err(|e| PolishError::Provider(format!("http send: {e}")))?;

        let status = resp.status();
        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            return Err(PolishError::Provider(format!(
                "http {status}: {}",
                truncate(&body, 300)
            )));
        }

        let parsed: ChatResponse = resp
            .json()
            .await
            .map_err(|e| PolishError::Provider(format!("decode response: {e}")))?;

        parsed
            .choices
            .into_iter()
            .next()
            .map(|c| c.message.content)
            .ok_or_else(|| PolishError::Provider("response had no choices".into()))
    }
}

fn build_user_message(req: &PolishRequest) -> String {
    let mut buf = String::with_capacity(req.raw.len() + 256);

    if !req.context_before.is_empty() {
        buf.push_str("[光标前 50 字]\n");
        buf.push_str(&req.context_before);
        buf.push_str("\n\n");
    }

    if !req.active_lexicon_ids.is_empty() {
        buf.push_str("[启用词库]\n");
        buf.push_str(&req.active_lexicon_ids.join(", "));
        buf.push_str("\n\n");
    }

    if !req.user_corrections.is_empty() {
        buf.push_str("[最近用户修正]\n");
        // Cap to 10 most-recent so the prompt doesn't blow up.
        for c in req.user_corrections.iter().rev().take(10).rev() {
            buf.push_str(&format!("- {} → {}\n", c.raw, c.user_final));
        }
        buf.push('\n');
    }

    buf.push_str("[ASR 原文]\n");
    buf.push_str(&req.raw);
    buf
}

/// Some models wrap their output in code fences or quotes despite the
/// prompt telling them not to. Strip the most common cases.
fn strip_wrapping(s: &str) -> String {
    let trimmed = s.trim();
    // ```text\n...\n``` or ```...```
    if let Some(stripped) = trimmed.strip_prefix("```") {
        if let Some(end) = stripped.rfind("```") {
            let inner = &stripped[..end];
            // drop optional language tag on first line
            return inner
                .splitn(2, '\n')
                .last()
                .unwrap_or(inner)
                .trim()
                .to_string();
        }
    }
    if (trimmed.starts_with('"') && trimmed.ends_with('"'))
        || (trimmed.starts_with('「') && trimmed.ends_with('」'))
    {
        return trimmed[1..trimmed.len() - 1].trim().to_string();
    }
    trimmed.to_string()
}

fn format_reject(reason: RejectReason) -> String {
    match reason {
        RejectReason::TooMuchChange => "edit_ratio>0.30".into(),
        RejectReason::HallucinatedEntities(es) => format!("hallucinated entities: {es:?}"),
    }
}

fn truncate(s: &str, max_chars: usize) -> String {
    if s.chars().count() <= max_chars {
        s.to_string()
    } else {
        s.chars().take(max_chars).chain(['…']).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn strips_code_fence_wrapping() {
        assert_eq!(strip_wrapping("```\nhello world\n```"), "hello world");
        assert_eq!(strip_wrapping("```text\nhello\n```"), "hello");
        assert_eq!(strip_wrapping("\"hello\""), "hello");
        assert_eq!(strip_wrapping("hello"), "hello");
    }

    #[test]
    fn build_message_includes_context_when_present() {
        let req = PolishRequest {
            raw: "打开 V S Code".into(),
            context_before: "之前的内容".into(),
            active_lexicon_ids: vec!["code".into()],
            user_corrections: vec![],
        };
        let msg = build_user_message(&req);
        assert!(msg.contains("[光标前 50 字]"));
        assert!(msg.contains("之前的内容"));
        assert!(msg.contains("[启用词库]"));
        assert!(msg.contains("code"));
        assert!(msg.contains("[ASR 原文]"));
        assert!(msg.contains("打开 V S Code"));
    }

    #[test]
    fn build_message_omits_empty_sections() {
        let req = PolishRequest {
            raw: "hello".into(),
            ..Default::default()
        };
        let msg = build_user_message(&req);
        assert!(!msg.contains("[光标前 50 字]"));
        assert!(!msg.contains("[启用词库]"));
        assert!(!msg.contains("[最近用户修正]"));
        assert!(msg.contains("[ASR 原文]"));
    }
}
