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
    
    
 