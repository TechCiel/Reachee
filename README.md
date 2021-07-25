# Reachee

吉林大学通知爬虫，发送到 Telegram 频道、webhook 或自定义目的地。

以 WTFPL 授权开源。

## 使用说明

需要 Python 3.6+ ，先 `pip3 install requests beautifulsoup4` 。

请参照 `reachee-example.json` 建立配置文件 `reachee.json` 。

支持：
- 使用直接连接或 VPNS 连接 OA
- 发送格式化的通知到 Telegram 会话
- 以 JSON 或 form 形式发送通知到 Webhook
- 跳过标题含有关键字的通知
- 隐去含有关键字的通知内容
- 指定获取其他通知频道
- 通过 `reachee.service` 使用 systemd 管理

## 联系

欢迎开 issue 、pr ，或者到 [Telegram@JLULUG](https://t.me/JLULUG) 转转。
