from typing import List, Dict, Optional
import os
import json
import re
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
        """创建个人日报汇总提示词（使用与团队日报相同的结构化分析方式）"""
        # 系统提示词（与 create_single_team_report_prompt 相同）
        system_prompt = """你是一名资深项目管理分析助手（AI PM Analyst），擅长从项目经理的每日汇报中，
抽取结构化事实、判断项目态势、识别人员负载与潜在风险。

你的目标不是复述日报内容，而是：
- 还原项目真实进展状态
- 识别隐含的人力占用结构
- 判断项目是否存在延期、风险或假推进信号
- 给出偏保守、可解释的分析结论

如果信息不足，请明确标注"不确定"，不要自行脑补。"""
        
        # 用户提示词（与 create_single_team_report_prompt 相同，但适配个人日报格式）
        user_prompt = f"""以下是一名团队管理者的个人工作日报，内容采用固定输入模式：

【项目】：<项目名称>

1. 今天项目发生了什么关键变化？
2. 今天主要消耗人力在什么事情上？
3. 有什么让我不安心的地方？
4. 明天如果一切顺利，项目应该到什么状态？

日报内容：
{personal_content}
客户相关人员：
dahai: MyCoach 客户
Nicole: MyCoach 客户
公司成员：
左莹莹：产品经理
修文强：web 开发
刘俭俭：java 开发
请你完成以下分析任务，并严格按 JSON 结构输出。

【分析任务】

一、事实抽取（不做判断）
- 当前项目阶段（需求 / 设计 / 开发 / 联调 / 测试 / 验收 / 不确定）
- 今日关键事件列表（推进 / 卡点 / 决策 / 客户反馈）
- 明确提及的人员及其角色（如：研发 / 产品 / 测试 / PM）
- 每个角色今天主要投入的工作类型

二、人力占用与饱和度推断（基于内容信号，而非精确工时）
- 对每个被提及的角色，判断其当前占用状态：
  - 高负载（持续核心产出 / 被多个事项牵引）
  - 中等负载
  - 低负载 / 等待中
- 判断是否存在角色缺位（某阶段本应出现但未出现的角色）
- 判断是否存在单点风险（关键事项集中在少数人）

三、项目态势判断
- 项目整体健康度：green / yellow / red / unknown
- 是否存在以下信号（是 / 否 / 不确定）：
  - 假推进（人很忙但交付未逼近）
  - 隐性延期风险
  - 需求或决策不稳定
  - 外部依赖阻塞（客户 / 第三方）
- 当前最主要的风险描述（一句话）

四、短期预期一致性检查
- "明天如果一切顺利的状态"是否合理？
- 是否存在明显乐观偏差或前置条件未满足？

【输出要求】

- 仅输出 JSON，不要输出解释性文字
- 所有判断必须能从原文找到依据
- 若无法判断，请使用 "unknown" 或 "insufficient_information"
- JSON 格式示例：
{{
  "project_stage": "开发",
  "key_events": ["推进：完成了XX功能开发", "卡点：等待第三方接口"],
  "personnel": {{
    "研发": {{
      "work_type": "功能开发",
      "load_status": "高负载"
    }},
    "测试": {{
      "work_type": "等待中",
      "load_status": "低负载"
    }}
  }},
  "role_gaps": ["缺少产品角色参与"],
  "single_point_risk": false,
  "health_status": "yellow",
  "risk_signals": {{
    "fake_progress": false,
    "delay_risk": true,
    "requirement_unstable": false,
    "external_block": true
  }},
  "main_risk": "等待第三方接口可能导致延期",
  "tomorrow_expectation_check": {{
    "reasonable": false,
    "optimistic_bias": true,
    "missing_prerequisites": ["第三方接口未就绪"]
  }}
}}"""
        
        # 组合系统提示词和用户提示词
        prompt = f"""{system_prompt}

{user_prompt}"""
        
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
                    logger.info("调用AI处理个人日报...")
                    response = Application.call(
                        api_key=self.config.api_key,
                        app_id=self.config.app_id,
                        prompt=personal_prompt,
                        temperature=0.1
                    )
                    
                    if response.status_code == HTTPStatus.OK:
                        raw_output = response.output.text.strip()
                        logger.info(f"AI原始输出长度: {len(raw_output)} 字符")
                        logger.info(f"AI原始输出预览: {raw_output[:300]}...")
                        
                        # 尝试解析JSON
                        json_data = self._extract_json_from_text(raw_output)
                        if json_data:
                            logger.info("✅ 成功解析个人日报JSON数据")
                            # 转换为报告格式
                            personal_summary = self._convert_personal_json_to_report(json_data, raw_output)
                            logger.info(f"✅ JSON转换为报告格式完成，报告长度: {len(personal_summary)} 字符")
                        else:
                            logger.warning("⚠️ 无法解析JSON，使用原始输出")
                            personal_summary = raw_output
                        
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
                        raw_output = response.output.text.strip()
                        logger.info(f"AI原始输出长度: {len(raw_output)} 字符")
                        logger.info(f"AI原始输出预览: {raw_output[:300]}...")
                        
                        # 尝试解析JSON
                        json_data = self._extract_json_from_text(raw_output)
                        if json_data:
                            logger.info("✅ 成功解析JSON数据")
                            # 转换为报告格式
                            summary = self._convert_json_to_report(json_data, raw_output)
                            logger.info(f"✅ JSON转换为报告格式完成，报告长度: {len(summary)} 字符")
                        else:
                            logger.warning("⚠️ 无法解析JSON，使用原始输出")
                            summary = raw_output
                        
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
        """为单个团队成员日报创建AI提示词（使用新的结构化分析提示词）"""
        # 系统提示词
        system_prompt = """你是一名资深项目管理分析助手（AI PM Analyst），擅长从项目经理的每日汇报中，
抽取结构化事实、判断项目态势、识别人员负载与潜在风险。

你的目标不是复述日报内容，而是：
- 还原项目真实进展状态
- 识别隐含的人力占用结构
- 判断项目是否存在延期、风险或假推进信号
- 给出偏保守、可解释的分析结论

如果信息不足，请明确标注"不确定"，不要自行脑补。"""
        
        # 用户提示词
        user_prompt = f"""以下是一名项目经理的项目日报，内容采用固定输入模式：

【项目】：<项目名称>

1. 今天项目发生了什么关键变化？
2. 今天主要消耗人力在什么事情上？
3. 有什么让我不安心的地方？
4. 明天如果一切顺利，项目应该到什么状态？

日报内容：
{report['body']}

请你完成以下分析任务，并严格按 JSON 结构输出。

【分析任务】

一、事实抽取（不做判断）
- 当前项目阶段（需求 / 设计 / 开发 / 联调 / 测试 / 验收 / 不确定）
- 今日关键事件列表（推进 / 卡点 / 决策 / 客户反馈）
- 明确提及的人员及其角色（如：研发 / 产品 / 测试 / PM）
- 每个角色今天主要投入的工作类型

二、人力占用与饱和度推断（基于内容信号，而非精确工时）
- 对每个被提及的角色，判断其当前占用状态：
  - 高负载（持续核心产出 / 被多个事项牵引）
  - 中等负载
  - 低负载 / 等待中
- 判断是否存在角色缺位（某阶段本应出现但未出现的角色）
- 判断是否存在单点风险（关键事项集中在少数人）

三、项目态势判断
- 项目整体健康度：green / yellow / red / unknown
- 是否存在以下信号（是 / 否 / 不确定）：
  - 假推进（人很忙但交付未逼近）
  - 隐性延期风险
  - 需求或决策不稳定
  - 外部依赖阻塞（客户 / 第三方）
- 当前最主要的风险描述（一句话）

四、短期预期一致性检查
- "明天如果一切顺利的状态"是否合理？
- 是否存在明显乐观偏差或前置条件未满足？

【输出要求】

- 仅输出 JSON，不要输出解释性文字
- 所有判断必须能从原文找到依据
- 若无法判断，请使用 "unknown" 或 "insufficient_information"
- JSON 格式示例：
{{
  "project_stage": "开发",
  "key_events": ["推进：完成了XX功能开发", "卡点：等待第三方接口"],
  "personnel": {{
    "研发": {{
      "work_type": "功能开发",
      "load_status": "高负载"
    }},
    "测试": {{
      "work_type": "等待中",
      "load_status": "低负载"
    }}
  }},
  "role_gaps": ["缺少产品角色参与"],
  "single_point_risk": false,
  "health_status": "yellow",
  "risk_signals": {{
    "fake_progress": false,
    "delay_risk": true,
    "requirement_unstable": false,
    "external_block": true
  }},
  "main_risk": "等待第三方接口可能导致延期",
  "tomorrow_expectation_check": {{
    "reasonable": false,
    "optimistic_bias": true,
    "missing_prerequisites": ["第三方接口未就绪"]
  }}
}}"""
        
        # 组合系统提示词和用户提示词
        prompt = f"""{system_prompt}

{user_prompt}"""
        
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
            summaries_text += f"\n=== {summary['username']} 的项目分析报告 ===\n"
            summaries_text += summary['summary'] + "\n"
        
        prompt = f"""
你是一名资深项目管理分析助手，需要对多个团队成员的项目分析报告进行整体整合。

以下是团队成员的项目分析报告：

{summaries_text}

请按照以下格式输出整合后的团队工作总结：

### 3. 团队项目进展
（整合所有成员的项目进展，按项目维度重新组织，避免重复，突出关键进展）

### 4. 团队项目风险
（整合所有成员提到的风险和问题，按项目或风险类型分类，去除重复内容）

整合要求：
- 按项目或业务线重新组织内容，而不是简单按人员分组
- 合并相关的项目进展，避免内容重复
- 识别跨人员的协作项目，统一描述进展
- 从各成员的分析报告中提取关键信息（项目阶段、关键事件、风险信号等）
- 语言简洁专业，每个要点控制在30字以内
- 使用统一的格式：- 项目名：具体进展描述
- 如果某个分类下没有内容，写"无"
- 重点关注健康度为 yellow 或 red 的项目
- 汇总所有风险信号，突出需要管理层关注的问题
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
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """从文本中提取JSON内容"""
        try:
            # 尝试直接解析整个文本
            return json.loads(text)
        except json.JSONDecodeError:
            # 如果失败，尝试提取JSON部分
            # 查找第一个 { 和最后一个 }
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # 尝试查找代码块中的JSON
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            
            logger.warning("无法从AI输出中提取有效的JSON")
            return None
    
    def _convert_personal_json_to_report(self, json_data: Dict, original_summary: str = "") -> str:
        """将个人日报的JSON分析结果转换为可读的报告格式（使用与团队日报相同的结构）"""
        try:
            # 使用与团队日报相同的转换方法
            report = self._convert_json_to_report(json_data, original_summary)
            return report
            
        except Exception as e:
            logger.error(f"转换个人日报JSON到报告格式时出错: {e}")
            # 如果转换失败，返回原始摘要或简单格式
            if original_summary:
                return f"# 个人工作总结\n\n{original_summary}"
            return "# 个人工作总结\n\n（JSON解析失败，使用原始内容）"
    
    def _convert_json_to_report(self, json_data: Dict, original_summary: str = "") -> str:
        """将JSON分析结果转换为可读的报告格式"""
        try:
            report = "**项目分析报告：**\n\n"
            
            # 一、事实抽取
            report += "**一、事实抽取**\n"
            project_stage = json_data.get("project_stage", "unknown")
            report += f"- 当前项目阶段：{project_stage}\n"
            
            key_events = json_data.get("key_events", [])
            if key_events:
                report += "- 今日关键事件：\n"
                for event in key_events:
                    report += f"  • {event}\n"
            else:
                report += "- 今日关键事件：无\n"
            
            personnel = json_data.get("personnel", {})
            if personnel:
                report += "- 人员投入情况：\n"
                for role, info in personnel.items():
                    if isinstance(info, dict):
                        work_type = info.get("work_type", "未知")
                        load_status = info.get("load_status", "未知")
                        report += f"  • {role}：{work_type}（{load_status}）\n"
            else:
                report += "- 人员投入情况：无相关信息\n"
            
            # 二、人力占用与饱和度
            report += "\n**二、人力占用分析**\n"
            role_gaps = json_data.get("role_gaps", [])
            if role_gaps:
                report += "- 角色缺位：\n"
                for gap in role_gaps:
                    report += f"  • {gap}\n"
            else:
                report += "- 角色缺位：无\n"
            
            single_point_risk = json_data.get("single_point_risk", False)
            report += f"- 单点风险：{'是' if single_point_risk else '否'}\n"
            
            # 三、项目态势判断
            report += "\n**三、项目态势判断**\n"
            health_status = json_data.get("health_status", "unknown")
            status_map = {
                "green": "🟢 健康",
                "yellow": "🟡 需关注",
                "red": "🔴 有风险",
                "unknown": "❓ 不确定"
            }
            report += f"- 项目健康度：{status_map.get(health_status, health_status)}\n"
            
            risk_signals = json_data.get("risk_signals", {})
            if risk_signals:
                report += "- 风险信号：\n"
                signal_map = {
                    "fake_progress": "假推进",
                    "delay_risk": "隐性延期风险",
                    "requirement_unstable": "需求或决策不稳定",
                    "external_block": "外部依赖阻塞"
                }
                for key, desc in signal_map.items():
                    value = risk_signals.get(key, "不确定")
                    if isinstance(value, bool):
                        value = "是" if value else "否"
                    report += f"  • {desc}：{value}\n"
            
            main_risk = json_data.get("main_risk", "")
            if main_risk:
                report += f"- 主要风险：{main_risk}\n"
            else:
                report += "- 主要风险：无\n"
            
            # 四、短期预期一致性检查
            report += "\n**四、短期预期检查**\n"
            expectation_check = json_data.get("tomorrow_expectation_check", {})
            if expectation_check:
                reasonable = expectation_check.get("reasonable", True)
                report += f"- 预期合理性：{'合理' if reasonable else '存在偏差'}\n"
                
                optimistic_bias = expectation_check.get("optimistic_bias", False)
                if optimistic_bias:
                    report += "- 乐观偏差：是\n"
                
                missing_prerequisites = expectation_check.get("missing_prerequisites", [])
                if missing_prerequisites:
                    report += "- 缺失前置条件：\n"
                    for pre in missing_prerequisites:
                        report += f"  • {pre}\n"
            else:
                report += "- 预期合理性：无法判断\n"
            
            return report
            
        except Exception as e:
            logger.error(f"转换JSON到报告格式时出错: {e}")
            # 如果转换失败，返回原始摘要或简单格式
            if original_summary:
                return f"**项目分析报告：**\n\n{original_summary}"
            return "**项目分析报告：**\n\n（JSON解析失败，使用原始内容）"
    
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