# 编码高频考点 + 推荐题单

> 不追求题量，追求每个主题都能「看到题就知道用什么模板」。

## 1. 数组 / 双指针 / 滑动窗口

**核心模板**

```python
# 通用滑动窗口（变长）
left = 0
state = init_state()
ans = 0
for right in range(len(nums)):
    add(nums[right], state)
    while not valid(state):
        remove(nums[left], state)
        left += 1
    ans = max(ans, right - left + 1)
```

**必练题**
- Two Sum
- Container With Most Water
- 3Sum
- Longest Substring Without Repeating Characters
- Minimum Window Substring
- Sliding Window Maximum

## 2. 哈希表 / 前缀和

- Subarray Sum Equals K
- Longest Consecutive Sequence
- Group Anagrams
- LRU Cache（哈希 + 双链表，必背模板）

## 3. 栈 / 单调栈 / 单调队列

- Valid Parentheses
- Daily Temperatures
- Largest Rectangle in Histogram
- Trapping Rain Water
- Min Stack

## 4. 链表

- Reverse Linked List（迭代 + 递归两种都要会）
- Merge Two Sorted Lists
- Linked List Cycle II（快慢指针求入口的数学推导要能讲）
- Reorder List
- Copy List with Random Pointer

## 5. 二叉树 / BST

**必背模板**

```python
# 自底向上递归
def dfs(node):
    if not node: return base_case
    left = dfs(node.left)
    right = dfs(node.right)
    # 1. 用 left/right 计算「全局答案」并更新
    # 2. 返回「给父节点用的局部答案」
    return local_answer
```

- Binary Tree Level Order Traversal
- Lowest Common Ancestor
- Diameter of Binary Tree
- Validate BST
- Serialize and Deserialize Binary Tree
- Path Sum III

## 6. 图

- Number of Islands（DFS / BFS / 并查集 三解）
- Course Schedule I & II（拓扑排序）
- Word Ladder（BFS）
- Network Delay Time（Dijkstra）
- Number of Connected Components（并查集模板）

## 7. 堆 / Top-K

- Kth Largest Element in an Array
- Top K Frequent Elements
- Merge K Sorted Lists
- Find Median from Data Stream（双堆，必背）

## 8. 回溯

```python
def backtrack(path, choices):
    if is_leaf(path):
        ans.append(path[:])
        return
    for c in choices:
        if not valid(c, path): continue
        path.append(c)
        backtrack(path, next_choices(c, choices))
        path.pop()
```

- Subsets / Subsets II
- Permutations / Permutations II
- Combination Sum / II
- Word Search
- Palindrome Partitioning

## 9. 贪心 / 区间

- Merge Intervals
- Insert Interval
- Non-overlapping Intervals
- Meeting Rooms II
- Jump Game I & II

## 10. 动态规划

**思考路径**：定义状态 → 转移方程 → 初始化 → 遍历方向 → 优化空间

- Climbing Stairs / House Robber I & II
- Coin Change / Coin Change II
- Longest Increasing Subsequence（O(n log n) 解法要会）
- Word Break
- Edit Distance
- Longest Palindromic Substring
- Maximum Product Subarray
- Best Time to Buy and Sell Stock III / IV（状态机思路）

## 11. 字符串高级

- KMP / Rabin-Karp（至少看懂思想）
- Trie：Implement Trie / Word Search II

## 12. 位运算

- Single Number I & II
- Number of 1 Bits
- Sum of Two Integers（不用 +）

---

## 错题本字段（建议）

| 题号 | 标签 | 第一次用时 | 出错原因 | 模板归属 | 复习日期 |
|------|------|------------|----------|----------|----------|
|      |      |            |          |          |          |

> 「出错原因」分类：状态定义错 / 边界 / 算法选错 / 实现 bug / 没看清题
