#!/usr/bin/env python3
"""
邮件格式化模块
将Markdown格式的内容转换为美观的纯文本邮件格式
"""

import re
from datetime import datetime

class EmailFormatter:
    """邮件内容格式化器"""
    
    def __init__(self):
        pass
    
    def format_for_email(self, markdown_content: str) -> str:
        """将Markdown内容转换为美观的纯文本邮件格式"""
        
        # 移除Markdown语法，转换为纯文本
        content = self._convert_markdown_to_text(markdown_content)
        
        # 添加开头语
        content = "张总：\n您好！\n\n" + content
        
        # 美化格式
        formatted_content = self._beautify_text_format(content)
        
        return formatted_content
    
    def _convert_markdown_to_text(self, markdown_content: str) -> str:
        """转换Markdown语法为纯文本"""
        content = markdown_content
        
        # 处理标题
        content = re.sub(r'^# (.+)$', r'【\1】', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'▉ \1', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'◆ \1', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.+)$', r'▸ \1', content, flags=re.MULTILINE)
        
        # 处理粗体
        content = re.sub(r'\*\*(.+?)\*\*', r'【\1】', content)
        content = re.sub(r'__(.+?)__', r'【\1】', content)
        
        # 处理斜体
        content = re.sub(r'\*(.+?)\*', r'_\1_', content)
        
        # 处理列表
        content = re.sub(r'^- (.+)$', r'  • \1', content, flags=re.MULTILINE)
        content = re.sub(r'^\* (.+)$', r'  • \1', content, flags=re.MULTILINE)
        content = re.sub(r'^\+ (.+)$', r'  • \1', content, flags=re.MULTILINE)
        
        # 处理数字列表
        content = re.sub(r'^(\d+)\. (.+)$', r'  \1. \2', content, flags=re.MULTILINE)
        
        # 处理代码块
        content = re.sub(r'```[\s\S]*?```', '', content)
        content = re.sub(r'`(.+?)`', r'"\1"', content)
        
        # 处理链接
        content = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', content)
        
        return content
    
    
    def _beautify_text_format(self, content: str) -> str:
        """美化文本格式"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                formatted_lines.append('')
                continue
            
            # 处理主标题
            if line.startswith('【') and line.endswith('】'):
                formatted_lines.append('')
                formatted_lines.append('=' * 80)
                formatted_lines.append(f"{line:^80}")
                formatted_lines.append('=' * 80)
                formatted_lines.append('')
                continue
            
            # 处理二级标题
            if line.startswith('▉ '):
                formatted_lines.append('')
                formatted_lines.append('─' * 60)
                formatted_lines.append(f"  {line}")
                formatted_lines.append('─' * 60)
                continue
            
            # 处理三级标题
            if line.startswith('◆ '):
                formatted_lines.append('')
                formatted_lines.append(f"  {line}")
                formatted_lines.append('  ' + '·' * 50)
                continue
            
            # 处理四级标题
            if line.startswith('▸ '):
                formatted_lines.append('')
                formatted_lines.append(f"    {line}")
                continue
            
            # 处理列表项
            if line.startswith('  •'):
                formatted_lines.append(f"    {line}")
                continue
            
            # 处理数字列表
            if re.match(r'^\s*\d+\.', line):
                formatted_lines.append(f"    {line}")
                continue
            
            # 处理包含冒号的行（通常是项目名称）
            if ':' in line and not line.startswith('  '):
                formatted_lines.append(f"  ▪ {line}")
                continue
            
            # 处理普通文本
            if line:
                # 如果是数字开头的行，可能是金额或数据
                if re.match(r'^\d+', line) or '元' in line or '%' in line:
                    formatted_lines.append(f"    {line}")
                else:
                    formatted_lines.append(f"  {line}")
        
        return '\n'.join(formatted_lines)
    
    
    def create_html_version(self, markdown_content: str) -> str:
        """创建HTML版本的邮件内容（如果需要支持HTML邮件）"""
        # 基本的Markdown到HTML转换
        html_content = markdown_content
        
        # 转换标题
        html_content = re.sub(r'^# (.+)$', r'<h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2 style="color: #34495e; margin-top: 25px;">\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.+)$', r'<h3 style="color: #7f8c8d; margin-top: 20px;">\1</h3>', html_content, flags=re.MULTILINE)
        
        # 转换粗体
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #2980b9;">\1</strong>', html_content)
        
        # 转换列表
        html_content = re.sub(r'^- (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
        
        # 转换换行
        html_content = html_content.replace('\n', '<br>\n')
        
        # 添加HTML框架
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>团队日报汇总</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 25px; }}
        h3 {{ color: #7f8c8d; margin-top: 20px; }}
        li {{ margin: 5px 0; }}
        .header {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .footer {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>📊 团队日报汇总</h2>
        <p>生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
    </div>
    
    {html_content}
    
    <div class="footer">
        <p>本邮件由智能日报系统自动生成 | 技术支持: AI自动化处理</p>
    </div>
</body>
</html>
"""
        return html_template 