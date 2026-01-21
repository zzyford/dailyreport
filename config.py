import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class EmailConfig(BaseModel):
    """邮箱配置"""
    smtp_host: str = "smtp.sunfield.mobi"
    smtp_port: int = 465
    imap_host: str = "imap.sunfield.mobi"
    imap_port: int = 993
    username: str
    password: str
    use_ssl: bool = True

class AIConfig(BaseModel):
    """AI配置"""
    api_key: str
    base_url: str = "https://dashscope.aliyuncs.com/api/v1/"
    app_id: str = ""  # 百炼平台应用ID
    max_tokens: int = 200000

class ReportConfig(BaseModel):
    """日报配置"""
    report_time: str = "09:00"  # 发送时间
    collect_days: int = 1  # 收集几天内的邮件
    report_subject_keywords: List[str] = ["日报","项目进度"]  # 搜索关键词
    report_recipients: List[str]  # 日报接收人邮箱列表
    report_from_emails: List[str]  # 需要收集日报的邮箱列表

class Config:
    """全局配置"""
    def __init__(self):
        self.email = EmailConfig(
            username=os.getenv("EMAIL_USERNAME", ""),
            password=os.getenv("EMAIL_PASSWORD", "")
        )
        
        # 从环境变量读取 max_tokens，默认为 8000（支持多项目长输出）
        max_tokens = int(os.getenv("DASHSCOPE_MAX_TOKENS", "80000"))
        self.ai = AIConfig(
            api_key=os.getenv("DASHSCOPE_API_KEY", ""),
            base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/"),
            app_id=os.getenv("DASHSCOPE_APP_ID", ""),
            max_tokens=max_tokens
        )
        
        # 处理日报配置 - 完全依赖环境变量，不使用硬编码邮箱
        recipients = os.getenv("REPORT_RECIPIENTS", "")
        from_emails = os.getenv("REPORT_FROM_EMAILS", "")
        
        self.report = ReportConfig(
            report_recipients=recipients.split(",") if recipients else [],
            report_from_emails=from_emails.split(",") if from_emails else [],
            report_time=os.getenv("REPORT_TIME", "09:00")
        )

# 全局配置实例
config = Config() 