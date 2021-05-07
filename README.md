# Reachee

吉林大学通知爬虫，发送到 Telegram 频道。

以 WTFPL 授权开源。

## 使用说明

需要 Python 3.6+ ，先 `pip3 install requests lxml` 。

需要使用吉大邮箱和密码以访问 VPN ，同时注意填写 bot token 和你的频道。

支持指定 OA 的通知栏目，支持过滤含指定词汇的通知。

可以参考 `reachee.service` 建立 systemd 服务。

若提示证书错误，请将 `ca.crt` 文件更新为 VPNS 的证书链。

## 联系

欢迎开 issue 、pr ，随缘处理。
