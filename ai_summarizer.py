from typing import List, Dict
import os
from http import HTTPStatus
from dashscope import Application
from loguru import logger
from config import AIConfig

class AISummarizer:
    """AI日报汇总器"""
    
    def __init__(self, ai_config: AIConfig):
        self.config = ai_config
    
    def format_reports_for_ai(self, reports: List[Dict]) -> str:
        """格式化日报数据供AI处理"""
        formatted_text = "以下是收集到的团队日报内容：\n\n"
        
        for i, report in enumerate(reports, 1):
            formatted_text += f"=== 日报 {i} ===\n"
            formatted_text += f"发送人: {report['from']}\n"
            formatted_text += f"主题: {report['subject']}\n"
            formatted_text += f"日期: {report['date']}\n"
            formatted_text += f"内容:\n{report['body']}\n\n"
        
        return formatted_text
    
    def create_summary_prompt(self, reports_text: str) -> str:
        """创建汇总提示词"""
        prompt = f"""
请根据以下团队日报内容，生成一份综合的团队工作汇总报告。

要求：
1. 总结团队整体的工作进展和成果
2. 提取关键的项目进展信息
3. 识别需要关注的问题和风险
4. 总结下一步的工作计划
5. 保持专业、简洁的语言风格
6. 按照以下结构组织内容：
   - 工作概览
   - 主要成果
   - 项目进展
   - 问题与风险
   - 下一步计划

团队日报内容：
{reports_text}

请生成汇总报告：
"""
        return prompt
    
    def summarize_reports(self, reports: List[Dict]) -> str:
        """汇总日报"""
        if not reports:
            return "今日暂无团队日报内容。"
        
        try:
            # 格式化报告内容
            reports_text = self.format_reports_for_ai(reports)
            
            # 创建提示词
            prompt = self.create_summary_prompt(reports_text)
            
            logger.info("开始调用阿里云百炼AI进行日报汇总...")
            
            if not self.config.app_id:
                logger.error("DASHSCOPE_APP_ID 未配置，无法调用AI服务")
                return self.create_simple_summary(reports)
            
            # 调用阿里云百炼API
            response = Application.call(
                api_key=self.config.api_key,
                app_id=self.config.app_id,
                prompt=prompt
            )
            
            if response.status_code != HTTPStatus.OK:
                logger.error(f"AI调用失败: code={response.status_code}, message={response.message}")
                logger.error(f"request_id={response.request_id}")
                return self.create_simple_summary(reports)
            
            summary = response.output.text.strip()
            logger.info("AI日报汇总完成")
            
            return summary
            
        except Exception as e:
            logger.error(f"AI汇总失败: {e}")
            # 返回简单的汇总作为备选
            return self.create_simple_summary(reports)
    
    def create_simple_summary(self, reports: List[Dict]) -> str:
        """创建简单的汇总（AI失败时的备选方案）"""
        summary = "=== 团队日报汇总 ===\n\n"
        summary += f"今日收集到 {len(reports)} 份日报\n\n"
        
        summary += "=== 日报详情 ===\n"
        for i, report in enumerate(reports, 1):
            summary += f"\n{i}. {report['from']} - {report['subject']}\n"
            # 截取前200字符作为摘要
            body_preview = report['body'][:200]
            if len(report['body']) > 200:
                body_preview += "..."
            summary += f"   {body_preview}\n"
        
        return summary
    
    def generate_daily_report_template(self) -> str:
        """生成日报模板"""
        template = """
=== 个人日报 ===

📅 日期: {date}

📋 今日工作内容:
• 

✅ 完成事项:
• 

📈 工作进展:
• 

⚠️ 遇到问题:
• 

📝 明日计划:
• 

💡 其他说明:
• 

---
此邮件由日报系统自动生成
"""
        return template 