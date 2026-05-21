# Week 2：进阶算法 + 系统设计入场

> 目标：把 BFS/DFS、堆、回溯、DP 这些高频中等以上题打通；同时让系统设计有「对话起手式」。

## 主题分布

| 天 | 编码主题 | 系统设计 / LP |
|----|----------|----------------|
| D8  | 图：BFS / DFS / 拓扑排序 | 阅读：可扩展性基础（垂直 vs 水平、无状态服务） |
| D9  | 堆 / Top-K / 多路归并 | 阅读：缓存（Cache-aside, write-through, TTL, eviction） |
| D10 | 回溯（子集 / 排列 / 组合） | 阅读：数据库（SQL vs NoSQL，索引，分片） |
| D11 | 区间 / 贪心 | 设计 #1：URL Shortener |
| D12 | DP I：一维 / 背包 | 设计 #2：Rate Limiter |
| D13 | DP II：二维 / 区间 / 状态压缩 | 设计 #3：News Feed / Timeline |
| D14 | 周复盘 + 1 场编码 mock（90 min）| LP 故事 #6–#10 |

## 系统设计「起手式」固化

每道系统设计题都按这 6 步走，不要乱：

1. **Clarify**：QPS、读写比、数据量、SLA、地域分布、是否离线/在线
2. **API**：列 3–5 个核心 endpoint
3. **Data model**：表 / 集合 / KV，键设计与索引
4. **High-level**：客户端 → CDN/LB → 服务 → 缓存 → DB / 队列
5. **Scale & bottleneck**：哪里会先挂？怎么分片 / 加缓存 / 异步化
6. **Trade-offs**：CAP、一致性级别、成本、复杂度

## Week 2 出口标准

- [ ] 能 35 min 内讲完 URL Shortener 的完整方案（含分片与冲突处理）
- [ ] DP 中等题不再「看了答案才想得到状态定义」≥ 70%
- [ ] LP 故事数量达到 10 个，每个能在 90 秒内讲完
