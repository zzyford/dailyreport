#!/usr/bin/env python3
"""
日报系统Web应用
包含富文本编辑器和AI汇总功能，以及后台定时任务
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime, date, timedelta
import json
import logging
import threading
import time
import schedule
import random
from email_handler import EmailHandler
from ai_summarizer import AISummarizer
from email_formatter import EmailFormatter
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 数据库配置
DATABASE = 'daily_reports.db'

# 全局配置
config = Config()

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建用户输入内容表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建生成的日报表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            user_content TEXT NOT NULL,
            email_content TEXT,
            final_report TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建定时任务日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduler_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_date TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            email_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_content_for_date(target_date: str) -> tuple:
    """
    获取指定日期的用户内容，如果没有则获取最近的一份
    返回 (content, actual_date, is_fallback)
    """
    conn = get_db_connection()
    
    # 首先尝试获取指定日期的内容
    user_content_row = conn.execute(
        'SELECT content, date FROM user_content WHERE date = ? ORDER BY updated_at DESC LIMIT 1',
        (target_date,)
    ).fetchone()
    
    if user_content_row and user_content_row['content'].strip():
        conn.close()
        return user_content_row['content'], user_content_row['date'], False
    
    # 如果指定日期没有内容，获取最近的一份
    logger.info(f"指定日期 {target_date} 没有用户内容，尝试获取最近的内容...")
    
    recent_content_row = conn.execute(
        'SELECT content, date FROM user_content WHERE content IS NOT NULL AND content != "" ORDER BY date DESC, updated_at DESC LIMIT 1'
    ).fetchone()
    
    conn.close()
    
    if recent_content_row and recent_content_row['content'].strip():
        logger.info(f"使用 {recent_content_row['date']} 的内容作为备用")
        return recent_content_row['content'], recent_content_row['date'], True
    
    return "", target_date, False

class BackgroundScheduler:
    """后台定时任务调度器"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.next_random_time = None
        self.daily_job = None
        
    def scheduled_task(self):
        """定时执行的任务"""
        try:
            logger.info("定时任务开始执行...")
            task_date = date.today().strftime('%Y-%m-%d')
            
            # 获取邮件内容
            email_handler = EmailHandler(config.email)
            email_reports = email_handler.collect_reports(
                from_emails=config.report.report_from_emails,
                subject_keywords=config.report.report_subject_keywords,
                days=1
            )
            
            if email_reports:
                # 格式化邮件内容
                email_content = "\n\n".join([
                    f"【{report['from']}的日报】\n主题: {report['subject']}\n内容: {report['body']}"
                    for report in email_reports
                ])
                
                # 获取用户输入的内容（如果当天没有则使用最近的一份）
                user_content, actual_date, is_fallback = get_user_content_for_date(task_date)
                
                if is_fallback and user_content.strip():
                    logger.info(f"定时任务使用备用内容：来自 {actual_date} 的工作内容")
                
                conn = get_db_connection()
                
                # 合并内容
                if user_content.strip():
                    combined_content = f"""
=== 个人工作内容 ===
{user_content}

=== 团队邮件日报 ===
{email_content}
"""
                else:
                    combined_content = f"""
=== 团队邮件日报 ===
{email_content}
"""
                
                # AI汇总
                ai_summarizer = AISummarizer(config.ai)
                final_report = ai_summarizer.summarize_reports([{
                    'from': '自动汇总',
                    'subject': '定时日报汇总',
                    'body': combined_content,
                    'date': task_date
                }])
                
                # 保存到数据库
                conn.execute(
                    'INSERT INTO generated_reports (date, user_content, email_content, final_report) VALUES (?, ?, ?, ?)',
                    (task_date, user_content, email_content, final_report)
                )
                
                # 记录任务日志
                conn.execute(
                    'INSERT INTO scheduler_logs (task_date, status, message, email_count) VALUES (?, ?, ?, ?)',
                    (task_date, 'success', f'成功汇总{len(email_reports)}份邮件日报', len(email_reports))
                )
                
                conn.commit()
                conn.close()
                
                logger.info(f"定时任务执行成功，汇总了{len(email_reports)}份邮件日报")
                
                # 如果配置了收件人，可以自动发送邮件
                if config.report.report_recipients:
                    try:
                        # 使用邮件格式化器美化内容
                        email_formatter = EmailFormatter()
                        formatted_content = email_formatter.format_for_email(final_report)
                        
                        email_handler.send_email(
                            to_emails=config.report.report_recipients,
                            subject=f"团队日报汇总 - {task_date}",
                            content=formatted_content,
                            content_type="plain"
                        )
                        logger.info("定时日报邮件发送成功")
                    except Exception as e:
                        logger.error(f"定时日报邮件发送失败: {e}")
            else:
                # 记录无邮件的情况
                conn = get_db_connection()
                conn.execute(
                    'INSERT INTO scheduler_logs (task_date, status, message, email_count) VALUES (?, ?, ?, ?)',
                    (task_date, 'no_emails', '未收集到邮件日报', 0)
                )
                conn.commit()
                conn.close()
                logger.info("定时任务执行完成，但未收集到邮件日报")
                
        except Exception as e:
            logger.error(f"定时任务执行失败: {e}")
            # 记录错误日志
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO scheduler_logs (task_date, status, message, email_count) VALUES (?, ?, ?, ?)',
                (date.today().strftime('%Y-%m-%d'), 'error', str(e), 0)
            )
            conn.commit()
            conn.close()
    
    def generate_random_time(self):
        """生成21:00-22:00之间的随机时间"""
        # 21:00:00 到 21:59:59 之间的随机时间
        hour = 21
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        random_time = f"{hour:02d}:{minute:02d}:{second:02d}"
        return random_time
    
    def schedule_next_random_task(self):
        """安排下一次随机时间的任务"""
        # 清除之前的任务
        if self.daily_job:
            schedule.cancel_job(self.daily_job)
        
        # 生成新的随机时间
        self.next_random_time = self.generate_random_time()
        
        # 设置新的定时任务
        self.daily_job = schedule.every().day.at(self.next_random_time).do(self.execute_and_reschedule)
        
        logger.info(f"下一次日报发送时间已设置为: {self.next_random_time}")
        
        # 保存到数据库以便Web界面显示
        try:
            conn = get_db_connection()
            # 记录下次执行时间
            today = date.today().strftime('%Y-%m-%d')
            conn.execute(
                'INSERT OR REPLACE INTO scheduler_logs (task_date, status, message, email_count) VALUES (?, ?, ?, ?)',
                (today + '_schedule', 'scheduled', f'下次执行时间: {self.next_random_time}', 0)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存调度信息失败: {e}")
    
    def execute_and_reschedule(self):
        """执行任务并重新安排下一次"""
        try:
            # 执行日报任务
            self.scheduled_task()
            
            # 立即安排明天的随机时间
            self.schedule_next_random_task()
            
        except Exception as e:
            logger.error(f"执行任务并重新安排失败: {e}")
            # 即使任务失败，也要安排下一次
            self.schedule_next_random_task()
    
    def run_scheduler(self):
        """运行调度器"""
        logger.info("后台定时任务启动...")
        
        # 首次启动时安排随机时间任务
        self.schedule_next_random_task()
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # 每30秒检查一次（因为精确到秒）
            except Exception as e:
                logger.error(f"定时任务调度异常: {e}")
                time.sleep(30)
        
        logger.info("后台定时任务已停止")
    
    def start(self):
        """启动后台任务"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
            logger.info("后台定时任务已启动")
    
    def stop(self):
        """停止后台任务"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("后台定时任务已停止")

# 创建全局调度器实例
scheduler = BackgroundScheduler()

@app.route('/')
def index():
    """主页面"""
    today = date.today().strftime('%Y-%m-%d')
    
    # 获取今天的内容
    conn = get_db_connection()
    user_content = conn.execute(
        'SELECT * FROM user_content WHERE date = ? ORDER BY updated_at DESC LIMIT 1',
        (today,)
    ).fetchone()
    conn.close()
    
    current_content = user_content['content'] if user_content else ""
    
    return render_template('index.html', 
                         current_date=today,
                         current_content=current_content)

@app.route('/save_content', methods=['POST'])
def save_content():
    """保存用户输入的内容"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        report_date = data.get('date', date.today().strftime('%Y-%m-%d'))
        
        conn = get_db_connection()
        
        # 检查是否已存在今天的记录
        existing = conn.execute(
            'SELECT id FROM user_content WHERE date = ?',
            (report_date,)
        ).fetchone()
        
        if existing:
            # 更新现有记录
            conn.execute(
                'UPDATE user_content SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE date = ?',
                (content, report_date)
            )
        else:
            # 插入新记录
            conn.execute(
                'INSERT INTO user_content (date, content) VALUES (?, ?)',
                (report_date, content)
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '内容保存成功'})
        
    except Exception as e:
        logger.error(f"保存内容失败: {e}")
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """生成日报"""
    try:
        data = request.get_json()
        report_date = data.get('date', date.today().strftime('%Y-%m-%d'))
        
        # 获取用户输入的内容（如果当天没有则使用最近的一份）
        user_content, actual_date, is_fallback = get_user_content_for_date(report_date)
        
        if not user_content.strip():
            return jsonify({'success': False, 'message': '没有找到可用的工作内容，请先输入工作内容'})
        
        if is_fallback:
            logger.info(f"使用备用内容：来自 {actual_date} 的工作内容")
        
        conn = get_db_connection()
        
        # 获取邮件内容
        logger.info("开始获取邮件内容...")
        email_handler = EmailHandler(config.email)
        email_reports = email_handler.collect_reports(
            from_emails=config.report.report_from_emails,
            subject_keywords=config.report.report_subject_keywords,
            days=1
        )
        
        email_content = ""
        if email_reports:
            email_content = "\n\n".join([
                f"【{report['from']}的日报】\n主题: {report['subject']}\n内容: {report['body']}"
                for report in email_reports
            ])
            logger.info(f"获取到 {len(email_reports)} 份邮件日报")
        else:
            logger.info("未获取到邮件日报")
        
        # 不再需要合并内容，直接分离处理
        
        logger.info(f"=== 准备分离处理个人和团队内容 ===")
        logger.info(f"个人内容长度: {len(user_content)} 字符")
        logger.info(f"团队邮件数量: {len(email_reports) if email_reports else 0}")
        
        # AI分离汇总
        logger.info("开始AI分离汇总...")
        ai_summarizer = AISummarizer(config.ai)
        final_report = ai_summarizer.summarize_reports_separated(
            personal_content=user_content,
            team_reports=email_reports if email_reports else []
        )
        
        # 保存生成的日报
        conn.execute(
            'INSERT INTO generated_reports (date, user_content, email_content, final_report) VALUES (?, ?, ?, ?)',
            (report_date, user_content, email_content, final_report)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'report': final_report,
            'email_count': len(email_reports) if email_reports else 0,
            'content_source': {
                'date': actual_date,
                'is_fallback': is_fallback,
                'message': f"⚠️ 当天无内容，使用了 {actual_date} 的工作内容作为备用" if is_fallback else f"✅ 使用了 {actual_date} 的工作内容"
            }
        })
        
    except Exception as e:
        logger.error(f"生成日报失败: {e}")
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'})

@app.route('/scheduler_status')
def scheduler_status():
    """获取定时任务状态"""
    try:
        conn = get_db_connection()
        
        # 获取最近的任务日志
        recent_logs = conn.execute(
            'SELECT * FROM scheduler_logs ORDER BY created_at DESC LIMIT 10'
        ).fetchall()
        
        # 获取下次执行时间
        next_run = None
        if scheduler.next_random_time:
            # 计算下次执行的完整日期时间
            today = datetime.now()
            next_date = today.date()
            
            # 如果当前时间已经过了今天的随机时间，则显示明天的时间
            current_time = today.time()
            random_time_parts = scheduler.next_random_time.split(':')
            random_time = datetime.strptime(scheduler.next_random_time, '%H:%M:%S').time()
            
            if current_time > random_time:
                next_date = today.date() + timedelta(days=1)
            
            next_run = f"{next_date} {scheduler.next_random_time}"
        
        conn.close()
        
        logs = []
        for log in recent_logs:
            logs.append({
                'date': log['task_date'],
                'status': log['status'],
                'message': log['message'],
                'email_count': log['email_count'],
                'created_at': log['created_at']
            })
        
        return jsonify({
            'success': True,
            'scheduler_running': scheduler.running,
            'next_run': next_run,
            'recent_logs': logs
        })
        
    except Exception as e:
        logger.error(f"获取定时任务状态失败: {e}")
        return jsonify({'success': False, 'message': f'获取状态失败: {str(e)}'})

@app.route('/toggle_scheduler', methods=['POST'])
def toggle_scheduler():
    """启动/停止定时任务"""
    try:
        data = request.get_json()
        action = data.get('action', 'start')
        
        if action == 'start':
            scheduler.start()
            return jsonify({'success': True, 'message': '定时任务已启动'})
        elif action == 'stop':
            scheduler.stop()
            return jsonify({'success': True, 'message': '定时任务已停止'})
        else:
            return jsonify({'success': False, 'message': '无效的操作'})
            
    except Exception as e:
        logger.error(f"切换定时任务状态失败: {e}")
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'})

@app.route('/history')
def history():
    """历史记录页面"""
    conn = get_db_connection()
    reports = conn.execute(
        'SELECT * FROM generated_reports ORDER BY created_at DESC LIMIT 50'
    ).fetchall()
    conn.close()
    
    return render_template('history.html', reports=reports)

@app.route('/api/history')
def api_history():
    """获取历史记录API"""
    conn = get_db_connection()
    reports = conn.execute(
        'SELECT date, final_report, created_at FROM generated_reports ORDER BY created_at DESC LIMIT 20'
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'date': report['date'],
        'content': report['final_report'],
        'created_at': report['created_at']
    } for report in reports])

@app.route('/send_history_email', methods=['POST'])
def send_history_email():
    """发送历史日报邮件"""
    try:
        data = request.get_json()
        report_date = data.get('date')
        report_content = data.get('content')
        password = data.get('password')
        
        # 验证密码
        if password != '12345678':
            return jsonify({'success': False, 'message': '密码错误'})
        
        if not report_date or not report_content:
            return jsonify({'success': False, 'message': '缺少必要参数'})
        
        # 检查是否配置了收件人
        if not config.report.report_recipients:
            return jsonify({'success': False, 'message': '未配置邮件收件人'})
        
        # 将HTML内容转换为纯文本
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(report_content, 'html.parser')
        text_content = soup.get_text()
        
        # 使用邮件格式化器美化内容
        email_formatter = EmailFormatter()
        formatted_content = email_formatter.format_for_email(text_content)
        
        # 发送邮件
        email_handler = EmailHandler(config.email)
        success = email_handler.send_email(
            to_emails=config.report.report_recipients,
            subject=f"Apple 日报汇总 - {report_date} ",
            content=formatted_content,
            content_type="plain"
        )
        
        if success:
            logger.info(f"历史日报邮件发送成功: {report_date}")
            return jsonify({'success': True, 'message': '邮件发送成功'})
        else:
            return jsonify({'success': False, 'message': '邮件发送失败'})
            
    except Exception as e:
        logger.error(f"发送历史日报邮件失败: {e}")
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'})

def show_startup_info():
    """显示启动信息"""
    print("=" * 60)
    print("🚀 智能日报系统 - Web版启动中...")
    print("=" * 60)
    
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Web地址: http://localhost:5002")
    print(f"📧 邮箱配置: {config.email.username}")
    print(f"🤖 AI配置: 阿里云百炼 (App ID: {config.ai.app_id[:8]}...)")
    
    print("\n⏰ 智能定时功能:")
    print("   • 每天21:00-22:00随机时间自动发送日报")
    print("   • 精确到秒级，共3600种可能时间")
    print("   • 自动收集团队邮件并AI汇总")
    print("   • 可选自动发送给指定收件人")
    
    print(f"\n📬 邮件收集配置:")
    for email in config.report.report_from_emails:
        print(f"   • {email}")
    
    if config.report.report_recipients:
        print(f"\n📤 自动发送给:")
        for email in config.report.report_recipients:
            print(f"   • {email}")
    else:
        print(f"\n📤 自动发送: 未配置收件人")
    
    print("\n💡 功能特色:")
    print("   ✓ Web界面编辑和预览")
    print("   ✓ 智能模板快速插入")
    print("   ✓ 实时定时任务监控")
    print("   ✓ 历史记录管理")
    print("   ✓ 随机时间避免机械化")
    print("   ✓ 热更新支持，代码修改自动重载")
    
    print("\n🔧 操作指南:")
    print("   1. 在Web界面输入个人工作内容")
    print("   2. 系统会自动在随机时间收集邮件")
    print("   3. AI智能汇总并发送综合日报")
    print("   4. 可在Web界面查看状态和历史")
    
    print("\n" + "=" * 60)

def check_environment():
    """检查环境配置"""
    issues = []
    
    if not config.email.username:
        issues.append("❌ 邮箱用户名未配置")
    
    if not config.email.password:
        issues.append("❌ 邮箱密码未配置")
    
    if not config.ai.api_key:
        issues.append("❌ DASHSCOPE_API_KEY未配置")
    
    if not config.ai.app_id:
        issues.append("❌ DASHSCOPE_APP_ID未配置")
    
    if issues:
        print("⚠️  配置检查发现问题:")
        for issue in issues:
            print(f"   {issue}")
        print("\n请检查.env文件配置后重新启动")
        return False
    
    print("✅ 环境配置检查通过")
    return True

if __name__ == '__main__':
    import sys
    
    try:
        # 显示启动信息
        show_startup_info()
        
        # 检查环境配置
        if not check_environment():
            sys.exit(1)
        
        print("🔄 正在启动Web服务和智能定时任务...")
        
        # 初始化数据库
        init_database()
        
        # 自动启动定时任务（仅在主进程中启动，避免热更新时重复启动）
        import os
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            # 这是重载后的子进程，不启动定时任务
            logger.info("Web应用重载，跳过定时任务启动")
        else:
            # 这是主进程，启动定时任务
            scheduler.start()
            logger.info("Web应用启动，定时任务已自动启动")
        
        # 启动应用（启用热更新）
        print("🔥 热更新已启用，代码修改后会自动重载")
        print("🔧 按 Ctrl+C 停止服务")
        print("=" * 60)
        
        # 配置Flask日志级别，减少调试信息干扰
        import logging
        flask_log = logging.getLogger('werkzeug')
        flask_log.setLevel(logging.WARNING)  # 只显示警告和错误
        
        app.run(
            host='0.0.0.0', 
            port=5002, 
            debug=True,  # 启用调试模式
            use_reloader=True,  # 启用热更新
            threaded=True  # 启用多线程支持
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信号")
        print("📊 正在安全关闭智能定时任务...")
        scheduler.stop()
        print("✅ 智能日报系统已安全关闭")
        
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        logger.error(f"应用运行异常: {e}")
        scheduler.stop()
        sys.exit(1) 