import schedule
import time
from datetime import datetime
from loguru import logger
from report_system import DailyReportSystem
from config import config

class ReportScheduler:
    """日报定时任务调度器"""
    
    def __init__(self):
        self.report_system = DailyReportSystem()
        self.setup_logger()
    
    def setup_logger(self):
        """设置日志"""
        logger.add("logs/daily_report_{time:YYYY-MM-DD}.log", 
                  rotation="1 day", 
                  retention="30 days",
                  level="INFO")
    
    def run_daily_task(self):
        """执行日报任务"""
        logger.info(f"定时任务触发 - {datetime.now()}")
        
        try:
            success = self.report_system.run_daily_report_task()
            if success:
                logger.info("定时日报任务执行成功")
            else:
                logger.error("定时日报任务执行失败")
        
        except Exception as e:
            logger.error(f"定时任务执行异常: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每天在指定时间执行
        schedule.every().day.at(config.report.report_time).do(self.run_daily_task)
        logger.info(f"定时任务已设置，每天 {config.report.report_time} 执行")
        
        # 可以添加更多的定时任务
        # 例如：每周一上午10点发送周报
        # schedule.every().monday.at("10:00").do(self.run_weekly_task)
    
    def run_scheduler(self):
        """运行调度器"""
        logger.info("日报系统启动...")
        self.setup_schedule()
        
        # 显示下一次运行时间
        next_run = schedule.next_run()
        logger.info(f"下一次任务执行时间: {next_run}")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
            except KeyboardInterrupt:
                logger.info("收到停止信号，正在关闭系统...")
                break
            except Exception as e:
                logger.error(f"调度器运行异常: {e}")
                time.sleep(60)
        
        logger.info("日报系统已停止")
    
    def run_once(self):
        """立即执行一次日报任务（用于测试）"""
        logger.info("手动执行日报任务...")
        self.run_daily_task()

if __name__ == "__main__":
    scheduler = ReportScheduler()
    
    # 检查命令行参数
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--run-once":
        # 立即执行一次
        scheduler.run_once()
    else:
        # 启动定时任务
        scheduler.run_scheduler() 