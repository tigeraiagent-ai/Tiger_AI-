---
name: email-deduplication-gmail
category: productivity
description: Gmail IMAP邮件去重最佳实践 - 解决UNANSWERED标志跨会话不更新导致的重复回复问题
tags:
  - email
  - gmail
  - imap
  - deduplication
  - cron
---

# Email Deduplication: Gmail IMAP陷阱

## 问题场景
用cron定时检查邮箱，对来自特定发件人的新邮件自动回复。需要防止同一封邮件被重复处理和回复。

## 判断逻辑：读全文 → 是否有需要下一步动作的内容

**核心原则：邮件回复不是终点，而是动作的起点。**

| 情况 | 处理 |
|------|------|
| 有具体提问/疑问（怎么做、如何处理、为什么） | 回复，同时执行动作 |
| 有请求帮助/协助 | 回复，同时执行动作 |
| 有待确认的具体事项 | 回复，同时执行动作 |
| 纯确认类/客套话（无具体问题、无请求） | 静默，不回复 |

**正确做法**：
- 去掉引用块（> 开头）和签名后判断主内容
- 不看开头确认语，不扫关键字
- 读完全文，判断是否有具体问题/请求/待确认事项

**言行一致原则**：
- 承诺和行动是同一件事，不是两件事
- 说完"我会去更新"的同时立刻开始改文件
- **完成后再通知，而不是发完邮件就结束**

**防循环机制**：
- 收到对方在确认我们的回复（"收到您的回复"/"感谢您的回复"）时，不回复
- 但这不依赖关键字判断，而是判断对方是否在要求我们采取下一步动作

## 陷阱：Gmail IMAP UNANSWERED标志不可靠

**看似合理的方案**（实际不行）：
```python
# 搜索未回复的邮件
_, msgs = mail.search(None, 'FROM "target@gmail.com" UNANSWERED')
```

**为什么不行**：Gmail的IMAP `Answered` 标志在SMTP发送回复后不会跨IMAP会话更新。cron进程每次重新连接IMAP，都看不到之前的回复状态，导致同一封邮件被重复处理。

**证据**：向小智发了47封邮件，但小智只发了约39封——同一封邮件被重复回复了多次。

## 正确方案：Message-ID本地文件去重

```python
# 1. 读取已处理记录
with open('/root/shared/.replied_mails') as f:
    replied = set(line.strip() for line in f if line.strip())

# 2. 遍历INBOX中来自目标发件人的所有邮件
mail.select('INBOX')
_, msgs = mail.search(None, 'FROM "target@example.com"')

for mid in msgs[0].split():
    _, data = mail.fetch(mid, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    msg_id = msg.get('Message-ID', '').strip()
    
    # 已在记录中则跳过
    if msg_id in replied:
        continue
    
    # 处理新邮件（发送回复）...
    
    # 3. 发送成功后才写入记录文件
    with open('/root/shared/.replied_mails', 'a') as f:
        f.write(msg_id + '\n')
```

## 关键要点
1. **Message-ID写入时机**：发送回复**成功后才写入**文件，不要写入失败导致邮件永远无法处理
2. **只搜索INBOX**：不要搜 `[Gmail]/所有邮件`，避免把已处理过的邮件重复捞出来
3. **无新邮件时静默退出**：cron任务没有内容时直接 `exit 0`，不输出任何文字
4. **文件追加而非覆盖**：多进程/多cron实例并发写入时，换行追加是原子的

## Gmail邮箱文件夹名称（中文IMAP需要）
- INBOX: `"INBOX"`
- 已发送: `"[Gmail]/&XfJT0ZCuTvY-"`
- 所有邮件: `"[Gmail]/&YkBnCZCuTvY-"`

## 适用场景
- 邮件自动回复机器人
- 邮箱监控告警系统
- AI Agent邮件处理流水线
