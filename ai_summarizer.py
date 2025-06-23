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

# 1. 产能情况
如果日报中包含季度产能数据，请按以下格式汇报：
本季度团队整体产能为 X 元（不含税，不含服务器成本）。

季度已开票金额（含税）为 X 元。
季度未开票金额（含税）为 X 元。

如果没有产能数据，则写：本次汇报无产能相关数据。

# 2. 今日工作内容
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
        """分别处理个人日报和团队日报（每个人分别处理避免上下文过长）"""
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
            
            # 处理团队日报 - 分别处理每个人的日报
            if team_reports:
                logger.info("=== 开始分别处理团队日报 ===")
                team_summary = self.process_team_reports_individually(team_reports)
            
            # 合并最终报告
            final_report = self.combine_summaries(personal_summary, team_summary)
            
            logger.info("=== AI分离汇总处理完成 ===")
            logger.info(f"最终报告长度: {len(final_report)} 字符")
            
            return final_report
            
        except Exception as e:
            logger.error(f"AI分离汇总失败: {e}")
            # 返回简单的汇总作为备选
            return self.create_fallback_summary(personal_content, team_reports)
    
    def process_team_reports_individually(self, team_reports: List[Dict]) -> str:
        """两阶段处理：先分别处理每个人的日报，再整体整合"""
        try:
            logger.info(f"开始两阶段处理 {len(team_reports)} 份团队日报")
            
            # 第一阶段：分别处理每个人的日报
            individual_summaries = []
            
            for i, report in enumerate(team_reports, 1):
                logger.info(f"=== 第一阶段：处理第 {i}/{len(team_reports)} 份团队日报 ===")
                logger.info(f"发件人: {report['from']}")
                logger.info(f"主题: {report['subject']}")
                logger.info(f"内容长度: {len(report['body'])} 字符")
                
                # 为单个日报创建AI提示词
                single_report_prompt = self.create_single_team_report_prompt(report)
                logger.info(f"单个日报提示词长度: {len(single_report_prompt)} 字符")
                
                if self.config.app_id:
                    logger.info(f"调用AI处理第 {i} 份日报...")
                    response = Application.call(
                        api_key=self.config.api_key,
                        app_id=self.config.app_id,
                        prompt=single_report_prompt,
                        temperature=0.1
                    )
                    
                    if response.status_code == HTTPStatus.OK:
                        summary = response.output.text.strip()
                        individual_summaries.append({
                            'from': report['from'],
                            'username': report['from'].split('@')[0],
                            'subject': report['subject'],
                            'summary': summary
                        })
                        logger.info(f"✅ 第 {i} 份日报AI汇总完成，汇总长度: {len(summary)} 字符")
                        logger.info(f"汇总预览: {summary[:200]}...")
                    else:
                        logger.error(f"❌ 第 {i} 份日报AI调用失败: {response.status_code}")
                        fallback_summary = f"AI处理失败，原始内容：{report['body'][:300]}..."
                        individual_summaries.append({
                            'from': report['from'],
                            'username': report['from'].split('@')[0],
                            'subject': report['subject'],
                            'summary': fallback_summary
                        })
                else:
                    logger.warning(f"⚠️ 未配置AI，使用原始内容作为第 {i} 份日报的汇总")
                    fallback_summary = f"原始内容：{report['body'][:300]}..."
                    individual_summaries.append({
                        'from': report['from'],
                        'username': report['from'].split('@')[0],
                        'subject': report['subject'],
                        'summary': fallback_summary
                    })
            
            # 第二阶段：整体整合所有个人汇总
            logger.info("=== 第二阶段：整体整合所有个人汇总 ===")
            final_team_summary = self.integrate_team_summaries(individual_summaries)
            logger.info(f"✅ 两阶段处理完成，最终汇总长度: {len(final_team_summary)} 字符")
            
            return final_team_summary
            
        except Exception as e:
            logger.error(f"❌ 两阶段处理失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self.create_simple_team_summary(team_reports)
    
    def create_single_team_report_prompt(self, report: Dict) -> str:
        """为单个团队成员日报创建AI提示词"""
        prompt = f"""
请对以下日报内容进行简洁的结构化总结：

{report['body']}

请严格按照以下格式输出：

**项目进展：**
- 项目1：简洁描述进展情况
- 项目2：简洁描述进展情况
- 项目3：简洁描述进展情况

**遇到问题/风险：**
- 问题1：简洁描述风险点
- 问题2：简洁描述风险点

要求：
- 每个要点控制在25字以内
- 直接列出项目名称和关键进展，去掉多余描述
- 如果某部分无内容，写"无"
- 严禁在输出中包含任何人名、邮箱或标识符号
- 输出内容不要包含发件人信息
- 只输出项目进展和风险两个部分
"""
        return prompt
    
    def integrate_team_summaries(self, individual_summaries: List[Dict]) -> str:
        """第二阶段：整体整合所有个人汇总"""
        try:
            logger.info(f"开始整合 {len(individual_summaries)} 个个人汇总")
            
            # 构建整合提示词
            integration_prompt = self.create_team_integration_prompt(individual_summaries)
            logger.info(f"整合提示词长度: {len(integration_prompt)} 字符")
            
            if self.config.app_id:
                logger.info("调用AI进行团队汇总整合...")
                response = Application.call(
                    api_key=self.config.api_key,
                    app_id=self.config.app_id,
                    prompt=integration_prompt,
                    temperature=0.1
                )
                
                if response.status_code == HTTPStatus.OK:
                    integrated_summary = response.output.text.strip()
                    logger.info(f"✅ 团队汇总整合完成，长度: {len(integrated_summary)} 字符")
                    return integrated_summary
                else:
                    logger.error(f"❌ 团队汇总整合AI调用失败: {response.status_code}")
                    # 降级到原来的合并方法
                    return self.combine_individual_summaries(individual_summaries)
            else:
                logger.warning("⚠️ 未配置AI，使用简单合并方法")
                return self.combine_individual_summaries(individual_summaries)
                
        except Exception as e:
            logger.error(f"❌ 团队汇总整合失败: {e}")
            # 降级到原来的合并方法
            return self.combine_individual_summaries(individual_summaries)
    
    def create_team_integration_prompt(self, individual_summaries: List[Dict]) -> str:
        """创建团队整合的AI提示词"""
        # 构建所有个人汇总的文本
        summaries_text = ""
        for i, summary in enumerate(individual_summaries, 1):
            summaries_text += f"\n=== {summary['username']} 的工作汇总 ===\n"
            summaries_text += summary['summary'] + "\n"
        
        prompt = f"""
请对以下团队成员的工作汇总进行整体整合，生成一份专业的团队工作总结：

{summaries_text}

请按照以下格式输出整合后的团队工作总结：

# 团队工作总结

# 1. 项目进展
（整合所有成员的项目进展，避免重复，突出关键进展）

# 2. 项目风险
（整合所有成员提到的风险和问题，去除重复内容）

整合要求：
- 按项目或业务线重新组织内容，而不是简单按人员分组
- 合并相关的项目进展，避免内容重复
- 识别跨人员的协作项目，统一描述进展
- 语言简洁专业，每个要点控制在30字以内
- 使用统一的格式：- 项目名：具体进展描述
- 如果某个分类下没有内容，写"无"
"""
        return prompt
    
    def combine_individual_summaries(self, individual_summaries: List[Dict]) -> str:
        """合并所有个人汇总为团队汇总（清晰格式版）"""
        logger.info(f"开始合并 {len(individual_summaries)} 个个人汇总")
        team_summary = "## 团队工作总结\n\n"
        
        # 1. 项目进展汇总
        logger.info("提取项目进展信息...")
        team_summary += "### 1. 项目进展\n\n"
        
        for summary in individual_summaries:
            username = summary['from'].split('@')[0]
            content = summary['summary']
            
            if '**项目进展：**' in content:
                start = content.find('**项目进展：**') + len('**项目进展：**')
                end = content.find('**遇到问题/风险：**')
                if end == -1:
                    end = len(content)
                progress = content[start:end].strip()
                
                if progress and progress not in ["无", "无相关内容"]:
                    # 清理格式，去掉多余的符号和空行，以及可能的邮箱格式
                    progress_lines = []
                    for line in progress.split('\n'):
                        line = line.strip()
                        if line and not self._contains_email_format(line):
                            progress_lines.append(line)
                    
                    if progress_lines:
                        team_summary += f"**{username}：**\n"
                        for line in progress_lines:
                            # 清理可能的邮箱格式残留
                            clean_line = self._clean_email_format(line)
                            # 确保每行都有合适的格式
                            if clean_line.startswith('-'):
                                team_summary += f"{clean_line}\n"
                            else:
                                team_summary += f"- {clean_line}\n"
                        team_summary += "\n"
                        logger.info(f"提取到 {username} 的项目进展")
        
        # 2. 项目风险汇总
        logger.info("提取项目风险信息...")
        team_summary += "### 2. 项目风险\n\n"
        
        has_risks = False
        for summary in individual_summaries:
            username = summary['from'].split('@')[0]
            content = summary['summary']
            
            if '**遇到问题/风险：**' in content:
                start = content.find('**遇到问题/风险：**') + len('**遇到问题/风险：**')
                risks = content[start:].strip()
                
                if risks and risks not in ["无", "无相关内容"]:
                    # 清理格式，去掉多余的符号和空行，以及可能的邮箱格式
                    risk_lines = []
                    for line in risks.split('\n'):
                        line = line.strip()
                        if line and not self._contains_email_format(line):
                            risk_lines.append(line)
                    
                    if risk_lines:
                        team_summary += f"**{username}：**\n"
                        for line in risk_lines:
                            # 清理可能的邮箱格式残留
                            clean_line = self._clean_email_format(line)
                            # 确保每行都有合适的格式
                            if clean_line.startswith('-'):
                                team_summary += f"{clean_line}\n"
                            else:
                                team_summary += f"- {clean_line}\n"
                        team_summary += "\n"
                        has_risks = True
                        logger.info(f"提取到 {username} 的风险信息")
        
        if not has_risks:
            team_summary += "暂无明显风险\n\n"
            logger.info("未找到项目风险信息")
        
        logger.info("团队汇总合并完成")
        return team_summary
    
    def _contains_email_format(self, text: str) -> bool:
        """检查文本是否包含邮箱格式"""
        # 检查是否包含类似 "姓名 <邮箱:" 的格式
        import re
        email_pattern = r'[^<]*<[^@]*@[^>]*:'
        return bool(re.search(email_pattern, text))
    
    def _clean_email_format(self, text: str) -> str:
        """清理文本中的邮箱格式"""
        import re
        # 移除类似 "姓名 <邮箱:" 的格式
        text = re.sub(r'[^<]*<[^@]*@[^>]*:\s*', '', text)
        # 移除可能的其他邮箱格式残留
        text = re.sub(r'<[^@]*@[^>]*>', '', text)
        text = re.sub(r'<[^>]*:', '', text)
        return text.strip()
    
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