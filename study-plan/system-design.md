# 系统设计骨架与高频题

## 通用 6 步法

每题都按这个顺序走，不要让面试官提醒你才补：

1. **Clarify scope**
   - QPS（read / write 分开估）
   - 数据量、保留期、单条大小
   - 一致性要求（强一致？最终一致？延迟容忍）
   - 地域 / 多活 / 离线
2. **API design**
   - 3–5 个核心 endpoint
   - 显式列出 request/response schema
3. **Data model**
   - 实体 + 字段 + 索引
   - 表/集合/KV 选型理由
4. **High-level architecture**
   - Client → CDN → LB → API Gateway → Service → Cache → DB / Queue / Storage
   - 把每条边的「协议、格式、是否同步」标清楚
5. **Scale & bottleneck**
   - 单点：DB 写、热点 Key、跨地域延迟
   - 解法：sharding、replication、cache、async、CDN、批量化
6. **Trade-offs & failure modes**
   - 一致性 vs 可用性
   - 成本 vs 性能
   - 复杂度 vs 可维护性
   - 当某组件挂掉，行为是什么？

## 容量估算速记

```text
1 day  ≈ 86,400 s ≈ 10^5 s
1 month ≈ 2.6 × 10^6 s
1 year  ≈ 3.15 × 10^7 s

1 KB ≈ 10^3 B
1 MB ≈ 10^6 B
1 GB ≈ 10^9 B
1 TB ≈ 10^12 B

DAU 100M, 每人每天 10 写  → 10^9 writes / day → ~12k QPS write
读写比 100:1                → ~1.2M QPS read
```

## 必备组件「拿来就用」

- **负载均衡**：L4 (TCP) vs L7 (HTTP)，Round-robin / Least-conn / Consistent hashing
- **缓存**：本地 cache（进程内）/ 分布式 cache（Redis）；Cache-aside（最常用）vs Write-through vs Write-back；TTL + 主动失效；防雪崩、击穿、穿透
- **数据库**
  - 关系型：强一致、复杂查询、事务；垂直拆分 + 主从 + 分库分表
  - NoSQL：KV (DynamoDB / Redis)、文档 (Mongo)、列族 (Cassandra)、宽表
  - 选型口诀：写多读少且 schema 多变 → NoSQL；强一致事务 → SQL
- **消息队列**：Kafka（高吞吐、持久化、顺序）、SQS（托管、简单）；用于削峰、解耦、异步、广播
- **存储**：对象存储（S3）放大文件，DB 放元数据
- **CDN**：静态资源 + 边缘缓存 + 视频
- **搜索**：Elasticsearch（倒排索引）
- **限流**：Token Bucket / Leaky Bucket / 固定窗口 / 滑动窗口
- **ID 生成**：UUID / Snowflake（时间 + 机器 + 序号）/ 号段
- **一致性哈希**：节点增减影响小，配合虚拟节点解决倾斜

## 必练题（每题至少手画一次架构图）

| # | 题目 | 重点考察 |
|---|------|----------|
| 1 | URL Shortener | ID 生成、KV 存储、读多写少缓存 |
| 2 | Rate Limiter | 限流算法、分布式状态、原子操作 |
| 3 | News Feed / Timeline | Push vs Pull vs 混合、Fanout |
| 4 | Chat (WhatsApp) | 长连接、推送、已读、离线消息 |
| 5 | Top K（实时榜单） | Stream + 近似算法（Count-Min Sketch） |
| 6 | Web Crawler | 去重（Bloom Filter）、礼貌策略、分布式队列 |
| 7 | Distributed File Storage | 分块、副本、一致性 |
| 8 | Ride Sharing (Uber) | 地理索引（GeoHash / Quadtree）、匹配算法 |
| 9 | Video Streaming (YouTube) | 转码流水线、CDN、自适应码率 |
| 10 | Online Code Judge | 沙箱隔离、队列、资源限制 |

## 反模式（面试官会扣分）

- 上来就画图，不 clarify
- 把所有东西塞进一个 monolith，不讲拆分
- 只说「加 Redis」不说为什么、放什么、失效策略
- 不做容量估算就谈分片
- 没讲故障场景就说「这样就稳了」
