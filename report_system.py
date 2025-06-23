from datetime import datetime
from typing import List, Dict
from loguru import logger
from email_handler import EmailHandler
from ai_summarizer import AISummarizer
from config import config

class DailyReportSystem:
    """日报系统主类"""
    
    def __init__(self):
        self.email_handler = EmailHandler(config.email)
        self.ai_summarizer = AISummarizer(config.ai)
        
    def collect_team_reports(self) -> List[Dict]:
        """收集团队日报"""
        logger.info("开始收集团队日报...")
        
        reports = self.email_handler.collect_reports(
            from_emails=config.report.report_from_emails,
            subject_keywords=config.report.report_subject_keywords,
            days=config.report.collect_days
        )
        
        return reports
    
    def generate_summary_report(self, reports: List[Dict]) -> str:
        """生成汇总日报"""
        logger.info("开始生成汇总日报...")
        
        # 使用AI汇总
        summary = self.ai_summarizer.summarize_reports(reports)
        
        # 添加报告头部信息
        current_time = datetime.now()
        header = f"""
=== 团队日报汇总 ===
生成时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
汇总日期: {current_time.strftime('%Y-%m-%d')}
收集报告数量: {len(reports)}

"""
        
        # 添加报告尾部信息
        footer = f"""

---
本报告由AI日报系统自动生成
系统时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        full_report = header + summary + footer
        return full_report
    
    def send_daily_report(self, report_content: str) -> bool:
        """发送日报"""
        logger.info("开始发送日报...")
        
        # 生成邮件主题
        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"团队日报汇总 - {current_date}"
        
        # 发送邮件
        success = self.email_handler.send_email(
            to_emails=config.report.report_recipients,
            subject=subject,
            content=report_content,
            content_type="plain"
        )
        
        if success:
            logger.info("日报发送成功")
        else:
            logger.error("日报发送失败")
        
        return success
    
    def run_daily_report_task(self) -> bool:
        """执行日报任务"""
        try:
            logger.info("=== 开始执行日报任务 ===")
            
            # 1. 收集团队日报
            reports = self.collect_team_reports()
            
            if not reports:
                logger.warning("未收集到任何日报")
                # 仍然发送一个空报告通知
                empty_report = f"""
=== 团队日报汇总 ===
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

今日暂无团队成员提交日报。

---
本报告由AI日报系统自动生成
"""
                return self.send_daily_report(empty_report)
            
            # 2. 生成汇总报告
            summary_report = self.generate_summary_report(reports)
            
            # 3. 发送日报
            success = self.send_daily_report(summary_report)
            
            logger.info("=== 日报任务执行完成 ===")
            return success
            
        except Exception as e:
            logger.error(f"日报任务执行失败: {e}")
            return False
    
    def test_email_connection(self) -> bool:
        """测试邮件连接"""
        try:
            logger.info("测试IMAP连接...")
            mail = self.email_handler.connect_imap()
            # 选择收件箱后再关闭
            mail.select('INBOX')
            mail.close()
            mail.logout()
            logger.info("IMAP连接测试成功")
            
            logger.info("测试SMTP连接...")
            smtp = self.email_handler.connect_smtp()
            smtp.quit()
            logger.info("SMTP连接测试成功")
            
            return True
            
        except Exception as e:
            logger.error(f"邮件连接测试失败: {e}")
            return False
    
    def test_ai_connection(self) -> bool:
        """测试AI连接"""
        try:
            logger.info("测试AI连接...")
            test_reports = [{
                'subject': '测试日报',
                'from': 'test@example.com',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'body': '这是一个测试日报内容。'
            }]
            
            summary = self.ai_summarizer.summarize_reports(test_reports)
            if summary:
                logger.info("AI连接测试成功")
                return True
            else:
                logger.error("AI返回空结果")
                return False
                
        except Exception as e:
            logger.error(f"AI连接测试失败: {e}")
            return False 