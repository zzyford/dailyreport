#!/usr/bin/env python3
"""
日报系统主程序
功能：自动收集团队日报，AI汇总后发送给指定人员
"""

import argparse
import sys
import os
from loguru import logger
from report_system import DailyReportSystem
from scheduler import ReportScheduler
from config import config

def setup_logging():
    """设置日志"""
    # 创建logs目录
    os.makedirs("logs", exist_ok=True)
    
    # 配置日志
    logger.add("logs/system_{time:YYYY-MM-DD}.log", 
              rotation="1 day", 
              retention="30 days",
              level="INFO")

def test_connections():
    """测试所有连接"""
    logger.info("=== 开始连接测试 ===")
    
    system = DailyReportSystem()
    
    # 测试邮件连接
    email_ok = system.test_email_connection()
    
    # 测试AI连接
    ai_ok = system.test_ai_connection()
    
    logger.info("=== 连接测试结果 ===")
    logger.info(f"邮件连接: {'✓' if email_ok else '✗'}")
    logger.info(f"AI连接: {'✓' if ai_ok else '✗'}")
    
    if email_ok and ai_ok:
        logger.info("所有连接测试通过，系统可以正常运行")
        return True
    else:
        logger.error("部分连接测试失败，请检查配置")
        return False

def run_once():
    """立即执行一次日报任务"""
    logger.info("立即执行日报任务...")
    
    system = DailyReportSystem()
    success = system.run_daily_report_task()
    
    if success:
        logger.info("日报任务执行成功")
    else:
        logger.error("日报任务执行失败")
    
    return success

def start_scheduler():
    """启动定时任务"""
    logger.info("启动定时日报系统...")
    
    scheduler = ReportScheduler()
    scheduler.run_scheduler()

def show_config():
    """显示当前配置"""
    print("=== 当前配置信息 ===")
    print(f"邮箱用户名: {config.email.username}")
    print(f"SMTP服务器: {config.email.smtp_host}:{config.email.smtp_port}")
    print(f"IMAP服务器: {config.email.imap_host}:{config.email.imap_port}")
    print(f"AI应用ID: {config.ai.app_id}")
    print(f"AI Base URL: {config.ai.base_url}")
    print(f"日报发送时间: {config.report.report_time}")
    print(f"日报接收人: {', '.join(config.report.report_recipients)}")
    print(f"日报来源: {', '.join(config.report.report_from_emails)}")
    print(f"主题关键词: {', '.join(config.report.report_subject_keywords)}")

def main():
    """主函数"""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="日报系统 - 自动收集、汇总、发送团队日报")
    parser.add_argument("--test", action="store_true", help="测试邮件和AI连接")
    parser.add_argument("--run-once", action="store_true", help="立即执行一次日报任务")
    parser.add_argument("--start", action="store_true", help="启动定时任务服务")
    parser.add_argument("--config", action="store_true", help="显示当前配置")
    
    args = parser.parse_args()
    
    # 检查配置
    if not config.email.username or not config.email.password:
        logger.error("邮箱配置不完整，请检查 .env 文件")
        sys.exit(1)
    
    if not config.ai.api_key:
        logger.error("DASHSCOPE_API_KEY 未配置，请检查 .env 文件")
        sys.exit(1)
    
    if not config.ai.app_id:
        logger.error("DASHSCOPE_APP_ID 未配置，请检查 .env 文件")
        sys.exit(1)
    
    if not config.report.report_recipients:
        logger.error("日报接收人未配置，请检查 .env 文件")
        sys.exit(1)
    
    try:
        if args.test:
            # 测试连接
            success = test_connections()
            sys.exit(0 if success else 1)
            
        elif args.run_once:
            # 立即执行一次
            success = run_once()
            sys.exit(0 if success else 1)
            
        elif args.start:
            # 启动定时任务
            start_scheduler()
            
        elif args.config:
            # 显示配置
            show_config()
            
        else:
            # 显示帮助
            parser.print_help()
            
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 