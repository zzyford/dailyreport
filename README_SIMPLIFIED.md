# 智能日报系统 - 使用指南

## 🚀 快速开始

### 方法一：一键启动
```bash
python run.py
```

### 方法二：直接启动
```bash
python web_app.py
```

## 📁 核心文件说明

### 主要文件
- `web_app.py` - **主程序**（Web应用+定时任务）
- `run.py` - 一键启动脚本

### 配置文件
- `.env` - 环境变量配置
- `config.py` - 配置类定义
- `requirements.txt` - 依赖包列表

### 功能模块
- `email_handler.py` - 邮件处理
- `ai_summarizer.py` - AI汇总
- `templates/` - HTML模板
- `static/` - 静态资源

### 测试脚本
- `test_random_schedule.py` - 测试随机时间生成
- `test_scheduler_now.py` - 测试调度器功能

## ⏰ 智能定时功能

- **随机时间**：每天21:00-22:00随机发送
- **精确到秒**：3600种可能的发送时间
- **自动重调度**：执行后自动安排下一天
- **Web监控**：实时查看状态和历史

## 🌐 Web界面功能

- **Markdown编辑器**：支持实时编辑和预览
- **快速模板**：工作、会议、项目、表格模板
- **智能汇总**：自动合并个人内容和团队邮件
- **历史管理**：查看所有生成的日报记录
- **定时监控**：实时监控定时任务状态

## 📧 邮件配置

系统支持自动收集团队邮件并智能汇总：

```env
# 收集邮件的来源
REPORT_FROM_EMAILS=user1@domain.com,user2@domain.com

# 自动发送的目标（可选）
REPORT_RECIPIENTS=boss@domain.com,manager@domain.com
```

## 🤖 AI配置

使用阿里云百炼平台进行智能汇总：

```env
DASHSCOPE_API_KEY=sk-your-api-key
DASHSCOPE_APP_ID=your-app-id
```

## 🔧 常用操作

### 启动系统
```bash
python web_app.py
# 或
python run.py
```

### 测试功能
```bash
# 测试随机时间
python test_random_schedule.py

# 测试调度器
python test_scheduler_now.py
```

### 查看配置
```bash
# 配置文件位置
cat .env
```

## 📱 访问地址

启动后访问：http://localhost:5002

## 💡 使用建议

1. **首次使用**：确保`.env`文件配置正确
2. **日常使用**：直接运行`python web_app.py`或`python run.py`
3. **定时任务**：系统启动后自动运行，无需额外操作
4. **手动生成**：可在Web界面随时手动生成日报
5. **状态监控**：通过Web界面实时查看定时任务状态

## 🎯 核心特色

- ✅ **一体化设计**：Web界面+定时任务集成在一个文件
- ✅ **智能随机**：避免机械化的固定时间发送
- ✅ **用户友好**：详细的启动信息和错误提示
- ✅ **功能完整**：编辑、预览、汇总、历史一应俱全
- ✅ **易于部署**：单文件包含所有核心功能 