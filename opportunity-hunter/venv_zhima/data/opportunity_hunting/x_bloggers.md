# X博主监控清单

## 数据源说明
- **syndication.twitter.com**: 官方接口，返回完整推文（但rate limit严格）
- **twiscan.com**: 备用接口，只返回$代码+截断上下文（部分覆盖）

## 已验证可用的博主（syndication有效）
| 用户名 | 专长 | 状态 |
|--------|------|------|
| aleabitoreddit | AI/半导体窭口+轧空 | ✅ 正常 |
| MarioNawfal | M&A/AI/全球宏观 | ⚠️ rate limit严格 |

## 候选博主（需虎哥确认后可加入）
| 用户名 | 专长 | 来源依据 |
|--------|------|---------|
| ValueCroc | 窭口垄断+光子学深度 | 搜索发现，twiscan无数据 |
| unusual_whales | 期权数据+机构流 | 华尔街知名 |
| ZeroHedge | 全球宏观+突发新闻 | 大V但非股票专用 |

## 待验证博主
（syndication拉取失败，需要手动验证或虎哥提供推文链接）

## 虎哥可参与的扩展方式
1. 虎哥直接发X推文链接给我 → 我分析 → 加入候选池
2. 虎哥推荐其他博主用户名 → 我验证+尝试拉取
3. 虎哥有Twitter账号 → 直接关注后转发给我

## 添加博主流程
```python
# 在x_hunter.py中修改TRACKED_ACCOUNTS
TRACKED_ACCOUNTS = [
    {"username": "aleabitoreddit", "name": "Serenity", "tags": ["AI/半导体", "窭口", "轧空"]},
    {"username": "MarioNawfal", "name": "Mario Nawfal", "tags": ["M&A/AI", "并购"]},
    # 虎哥确认后添加新博主
]
```

## 扩展计划
- 第1批: Serenity + MarioNawfal（正在验证）
- 第2批: ValueCroc + 其他窭口型博主
- 第3批: 轧空型博主（WSB风格）