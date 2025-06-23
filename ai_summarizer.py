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
    
    def create_personal_summary_prompt(self, personal_content: str) -> str:
        """创建个人日报汇总提示词"""
        prompt = f"""
你是一名团队管理者，需要向老板汇报工作。请根据以下个人工作日报内容，按照固定格式生成客观、简练的工作汇报：

个人工作日报内容：
{personal_content}

请严格按照以下格式生成汇报：

### 1. 产能情况
如果日报中包含季度产能数据，请按以下格式汇报：
本季度团队整体产能为 X 元（不含税，不含服务器成本）。

季度已开票金额（含税）为 X 元。
季度未开票金额（含税）为 X 元。
未开票金额如下：（含税）为 X 元。

如果没有产能数据，则写：本次汇报无产能相关数据。

### 2. 今日工作内容
今日主要完成了以下工作：

[按项目或任务逐条列出，格式为：项目名称：具体完成的工作内容。]

要求：
- 你是团队管理者，向老板汇报工作
- 语言客观、简练，不要有任何主观解读
- 完全基于原始内容进行客观阐述
- 不要添加评价性词汇或主观判断
- 严格按照提供的格式输出
- 如果某部分内容不存在，明确说明"无相关数据"或"无相关内容"
"""
        return prompt
    
    def create_team_summary_prompt(self, team_reports: str) -> str:
        """创建团队日报汇总提示词"""
        prompt = f"""
你是一名团队管理者，需要向老板汇报团队工作情况。请根据以下团队成员的邮件日报内容，按照固定格式生成客观、简练的团队工作汇报：

团队邮件日报内容：
{team_reports}

请严格按照以下格式生成汇报：


### 3. 团队项目进展
各项目进展情况如下：

[按项目名称分类，格式为：项目名称：具体进展情况。]

### 4. 团队项目风险
需要关注的问题和风险：

[如有风险或问题，按项目列出具体情况；如无明显风险则写：无需要特别关注的风险。]

要求：
- 你是团队管理者，向老板汇报团队工作
- 语言客观、简练，不要有任何主观解读
- 完全基于团队成员日报内容进行客观阐述
- 不要添加评价性词汇或主观判断
- 严格按照提供的格式输出
- 按项目维度整理信息，便于管理层了解情况
- 如果某部分内容不存在，明确说明"无相关数据"或"无相关内容"
"""
        return prompt
    
    def summarize_reports_separated(self, personal_content: str, team_reports: List[Dict]) -> str:
        """分别处理个人日报和团队日报"""
        try:
            logger.info(f"=== AI分离汇总处理开始 ===")
            logger.info(f"个人内容长度: {len(personal_content)} 字符")
            logger.info(f"团队报告数量: {len(team_reports)}")
            
            personal_summary = ""
            team_summary = ""
            
            # 处理个人日报
            if personal_content.strip():
                logger.info("=== 开始处理个人日报 ===")
                personal_prompt = self.create_personal_summary_prompt(personal_content)
                logger.info(f"个人日报提示词长度: {len(personal_prompt)} 字符")
                
                if self.config.app_id:
                    response = Application.call(
                        api_key=self.config.api_key,
                        app_id=self.config.app_id,
                        prompt=personal_prompt,
                        temperature=0.1
                    )
                    
                    if response.status_code == HTTPStatus.OK:
                        personal_summary = response.output.text.strip()
                        logger.info("个人日报AI汇总完成")
                    else:
                        logger.error(f"个人日报AI调用失败: {response.status_code}")
                        personal_summary = self.create_simple_personal_summary(personal_content)
                else:
                    personal_summary = self.create_simple_personal_summary(personal_content)
            
            # 处理团队日报
            if team_reports:
                logger.info("=== 开始处理团队日报 ===")
                team_reports_text = self.format_reports_for_ai(team_reports)
                team_prompt = self.create_team_summary_prompt(team_reports_text)
                logger.info(f"团队日报提示词长度: {len(team_prompt)} 字符")
                
                if self.config.app_id:
                    response = Application.call(
                        api_key=self.config.api_key,
                        app_id=self.config.app_id,
                        prompt=team_prompt,
                        temperature=0.1
                    )
                    
                    if response.status_code == HTTPStatus.OK:
                        team_summary = response.output.text.strip()
                        logger.info("团队日报AI汇总完成")
                    else:
                        logger.error(f"团队日报AI调用失败: {response.status_code}")
                        team_summary = self.create_simple_team_summary(team_reports)
                else:
                    team_summary = self.create_simple_team_summary(team_reports)
            
            # 合并最终报告
            final_report = self.combine_summaries(personal_summary, team_summary)
            
            logger.info("=== AI分离汇总处理完成 ===")
            logger.info(f"最终报告长度: {len(final_report)} 字符")
            
            return final_report
            
        except Exception as e:
            logger.error(f"AI分离汇总失败: {e}")
            # 返回简单的汇总作为备选
            return self.create_fallback_summary(personal_content, team_reports)
    
    def summarize_reports(self, reports: List[Dict]) -> str:
        """汇总日报 - 保持向后兼容"""
        if not reports:
            return "今日暂无日报内容。"
        
        # 这个方法保持不变，用于向后兼容
        return self.create_simple_summary(reports)
    
    def combine_summaries(self, personal_summary: str, team_summary: str) -> str:
        """合并个人和团队汇总"""
        final_report = ""
        
        if personal_summary:
            final_report += personal_summary + "\n\n"
        
        if team_summary:
            final_report += team_summary + "\n\n"
        
        if not personal_summary and not team_summary:
            final_report += "今日暂无日报内容。"
        
        return final_report
    
    def create_simple_personal_summary(self, personal_content: str) -> str:
        """创建简单的个人汇总（AI失败时的备选方案）"""
        summary = "## 个人工作总结\n\n"
        summary += "### 1. 产能情况\n"
        summary += "（AI汇总失败，请查看原始内容）\n\n"
        summary += "### 2. 今日工作内容\n"
        summary += f"{personal_content}\n"
        return summary
    
    def create_simple_team_summary(self, team_reports: List[Dict]) -> str:
        """创建简单的团队汇总（AI失败时的备选方案）"""
        summary = "## 团队工作总结\n\n"
        summary += f"今日收集到 {len(team_reports)} 份团队日报\n\n"
        
        summary += "### 1. 产能情况\n"
        summary += "（AI汇总失败，请查看原始邮件）\n\n"
        
        summary += "### 2. 项目进展\n"
        for i, report in enumerate(team_reports, 1):
            summary += f"{i}. {report['from']} - {report['subject']}\n"
            body_preview = report['body'][:150]
            if len(report['body']) > 150:
                body_preview += "..."
            summary += f"   {body_preview}\n\n"
        
        summary += "### 3. 项目风险\n"
        summary += "（需要人工梳理邮件内容）\n"
        
        return summary
    
    def create_fallback_summary(self, personal_content: str, team_reports: List[Dict]) -> str:
        """创建备选汇总（完全失败时）"""
        summary = "# 日报汇总\n\n"
        summary += "## 个人工作内容\n"
        summary += f"{personal_content}\n\n"
        
        if team_reports:
            summary += "## 团队邮件日报\n"
            for i, report in enumerate(team_reports, 1):
                summary += f"### {i}. {report['from']}\n"
                summary += f"**主题:** {report['subject']}\n"
                summary += f"**内容:** {report['body']}\n\n"
        
        return summary
    
    def get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
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