#!/usr/bin/env python3
"""
日报系统Web应用
包含富文本编辑器和AI汇总功能
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime, date
import json
import logging
from email_handler import EmailHandler
from ai_summarizer import AISummarizer
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 数据库配置
DATABASE = 'daily_reports.db'

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
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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
        
        # 获取用户输入的内容
        conn = get_db_connection()
        user_content_row = conn.execute(
            'SELECT content FROM user_content WHERE date = ? ORDER BY updated_at DESC LIMIT 1',
            (report_date,)
        ).fetchone()
        
        user_content = user_content_row['content'] if user_content_row else ""
        
        if not user_content.strip():
            return jsonify({'success': False, 'message': '请先输入工作内容'})
        
        # 获取邮件内容
        logger.info("开始获取邮件内容...")
        config = Config()
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
        
        # 合并内容
        combined_content = f"""
=== 个人工作内容 ===
{user_content}

=== 团队邮件日报 ===
{email_content if email_content else "暂无邮件日报"}
"""
        
        # AI汇总
        logger.info("开始AI汇总...")
        ai_summarizer = AISummarizer(config.ai)
        final_report = ai_summarizer.summarize_reports([{
            'from': '综合日报',
            'subject': '综合日报汇总',
            'body': combined_content,
            'date': report_date
        }])
        
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
            'email_count': len(email_reports) if email_reports else 0
        })
        
    except Exception as e:
        logger.error(f"生成日报失败: {e}")
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'})

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

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 启动应用
    app.run(host='0.0.0.0', port=5002, debug=True) 