import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import ssl
from loguru import logger
from bs4 import BeautifulSoup
from config import EmailConfig

class EmailHandler:
    """邮件处理器"""
    
    def __init__(self, email_config: EmailConfig):
        self.config = email_config
        
    def connect_imap(self) -> imaplib.IMAP4_SSL:
        """连接IMAP服务器"""
        try:
            if self.config.use_ssl:
                mail = imaplib.IMAP4_SSL(self.config.imap_host, self.config.imap_port)
            else:
                mail = imaplib.IMAP4(self.config.imap_host, self.config.imap_port)
            
            mail.login(self.config.username, self.config.password)
            logger.info("IMAP连接成功")
            return mail
        except Exception as e:
            logger.error(f"IMAP连接失败: {e}")
            raise
    
    def connect_smtp(self) -> smtplib.SMTP_SSL:
        """连接SMTP服务器"""
        try:
            if self.config.use_ssl:
                server = smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port)
            else:
                server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)
                server.starttls()
            
            server.login(self.config.username, self.config.password)
            logger.info("SMTP连接成功")
            return server
        except Exception as e:
            logger.error(f"SMTP连接失败: {e}")
            raise
    
    def decode_mime_words(self, s: str) -> str:
        """解码MIME编码的字符串"""
        decoded_parts = decode_header(s)
        decoded_string = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or 'utf-8')
            else:
                decoded_string += part
        return decoded_string
    
    def extract_text_from_html(self, html_content: str) -> str:
        """从HTML中提取纯文本"""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
    
    def get_email_body(self, msg) -> str:
        """获取邮件正文"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode('utf-8')
                        except:
                            try:
                                body = part.get_payload(decode=True).decode('gbk')
                            except:
                                body = str(part.get_payload(decode=True))
                        break
                    elif content_type == "text/html":
                        try:
                            html_content = part.get_payload(decode=True).decode('utf-8')
                        except:
                            try:
                                html_content = part.get_payload(decode=True).decode('gbk')
                            except:
                                html_content = str(part.get_payload(decode=True))
                        body = self.extract_text_from_html(html_content)
                        break
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                try:
                    body = msg.get_payload(decode=True).decode('utf-8')
                except:
                    try:
                        body = msg.get_payload(decode=True).decode('gbk')
                    except:
                        body = str(msg.get_payload(decode=True))
            elif content_type == "text/html":
                try:
                    html_content = msg.get_payload(decode=True).decode('utf-8')
                except:
                    try:
                        html_content = msg.get_payload(decode=True).decode('gbk')
                    except:
                        html_content = str(msg.get_payload(decode=True))
                body = self.extract_text_from_html(html_content)
        
        return body.strip()
    
    def collect_reports(self, 
                       from_emails: List[str], 
                       subject_keywords: List[str], 
                       days: int = 1) -> List[Dict]:
        """收集日报邮件"""
        reports = []
        mail = self.connect_imap()
        
        try:
            # 选择收件箱
            mail.select('INBOX')
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 搜索邮件
            date_criteria = start_date.strftime("%d-%b-%Y")
            search_criteria = f'(SINCE "{date_criteria}")'
            
            # 如果指定了发件人
            if from_emails:
                from_criteria = ' OR '.join([f'FROM "{email}"' for email in from_emails])
                search_criteria += f' ({from_criteria})'
            
            logger.info(f"搜索条件: {search_criteria}")
            status, messages = mail.search(None, search_criteria)
            
            if status != 'OK':
                logger.error("邮件搜索失败")
                return reports
            
            email_ids = messages[0].split()
            logger.info(f"找到 {len(email_ids)} 封邮件")
            
            for email_id in email_ids:
                try:
                    # 获取邮件
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    # 解析邮件
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # 获取邮件信息
                    subject = self.decode_mime_words(msg.get('Subject', ''))
                    from_addr = self.decode_mime_words(msg.get('From', ''))
                    date_str = msg.get('Date', '')
                    
                    # 检查主题是否包含关键词
                    if not any(keyword in subject for keyword in subject_keywords):
                        continue
                    
                    # 获取邮件正文
                    body = self.get_email_body(msg)
                    
                    if body:
                        reports.append({
                            'subject': subject,
                            'from': from_addr,
                            'date': date_str,
                            'body': body
                        })
                        logger.info(f"收集到日报: {subject} - {from_addr}")
                
                except Exception as e:
                    logger.error(f"处理邮件 {email_id} 时出错: {e}")
                    continue
            
        finally:
            mail.close()
            mail.logout()
        
        logger.info(f"共收集到 {len(reports)} 份日报")
        return reports
    
    def send_email(self, 
                   to_emails: List[str], 
                   subject: str, 
                   content: str, 
                   content_type: str = "plain") -> bool:
        """发送邮件"""
        try:
            server = self.connect_smtp()
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.config.username
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(content, content_type, 'utf-8'))
            
            # 发送邮件
            server.send_message(msg)
            server.quit()
            
            logger.info(f"邮件发送成功: {subject} -> {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False 