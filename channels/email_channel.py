"""邮件渠道:SMTP 发送。

QQ 邮箱:smtp.qq.com:465(SSL),密码用授权码(非登录密码)。
缺少 SMTP 环境变量时自动回退为打印到控制台(dry-run),方便本地调试。
"""
from __future__ import annotations
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from brief.registry import register_channel
from brief.base import Channel


@register_channel("email")
class EmailChannel(Channel):
    def __init__(self, subject_prefix: str = "[Brief]"):
        self.subject_prefix = subject_prefix

    def send(self, subject: str, content: str) -> None:
        host = os.environ.get("SMTP_HOST", "")
        port = int(os.environ.get("SMTP_PORT", "465"))
        user = os.environ.get("EMAIL_ADDRESS", "")
        pwd = os.environ.get("EMAIL_PASSWORD", "")
        to = os.environ.get("EMAIL_TO", "")
        full_subject = f"{self.subject_prefix} {subject}".strip()

        if not (host and user and pwd and to):
            self._dry_run(full_subject, to, content)
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = full_subject
        msg["From"] = user
        msg["To"] = to
        msg.attach(MIMEText(content, "html", "utf-8"))
        with smtplib.SMTP_SSL(host, port, timeout=30) as s:
            s.login(user, pwd)
            s.sendmail(user, [to], msg.as_string())
        print(f"[email] 已发送: {full_subject} -> {to}")

    @staticmethod
    def _dry_run(subject, to, content):
        import sys
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        print("=" * 64)
        print("[dry-run] SMTP 未配置,邮件内容如下:")
        print(f"Subject: {subject}")
        print(f"To: {to or '(未配置)'}")
        print("-" * 64)
        print(content)
        print("=" * 64)
