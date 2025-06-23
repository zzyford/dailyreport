# 日报系统

一个基于Python的自动化日报系统，支持从网易企业邮箱收集团队日报，使用AI进行汇总，并定时发送给指定人员。

## 功能特性

- 📧 **邮件集成**: 支持网易企业邮箱的IMAP收取和SMTP发送
- 🤖 **AI汇总**: 使用阿里云百炼平台智能汇总多份日报
- ⏰ **定时任务**: 每天定时自动执行日报收集和发送
- 📊 **智能处理**: 自动解析邮件内容，支持HTML和纯文本格式
- 🔍 **灵活筛选**: 支持按发件人、主题关键词、时间范围筛选
- 📝 **详细日志**: 完整的操作日志记录和错误跟踪

## 系统架构

```
日报系统
├── 邮件处理模块 (email_handler.py)
│   ├── IMAP邮件收取
│   └── SMTP邮件发送
├── AI汇总模块 (ai_summarizer.py)
│   ├── OpenAI API集成
│   └── 智能内容汇总
├── 定时任务模块 (scheduler.py)
│   ├── 定时任务调度
│   └── 任务执行管理
├── 配置管理 (config.py)
│   ├── 邮箱配置
│   ├── AI配置
│   └── 日报配置
└── 主程序 (main.py)
    ├── 命令行界面
    └── 系统管理
```

## 安装配置

### 1. 环境要求

- Python 3.8+
- 网易企业邮箱账号
- 阿里云百炼平台 API Key 和应用ID

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 网易企业邮箱配置
EMAIL_USERNAME=your-email@company.163.com
EMAIL_PASSWORD=your-email-password

# 阿里云百炼平台配置
DASHSCOPE_API_KEY=your-dashscope-api-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1/
DASHSCOPE_APP_ID=your-app-id

# 日报配置
REPORT_RECIPIENTS=boss@company.com,manager@company.com
REPORT_FROM_EMAILS=shaoyunfeng@sunfield.mobi,chenxi@sunfield.mobi,xugenli@sunfield.mobi
REPORT_TIME=09:00
```

## 使用方法

### 测试连接

在正式使用前，测试邮件和AI连接：

```bash
python main.py --test
```

### 立即执行一次

手动执行一次日报任务：

```bash
python main.py --run-once
```

### 启动定时服务

启动定时日报服务：

```bash
python main.py --start
```

### 查看配置

显示当前系统配置：

```bash
python main.py --config
```

## 配置说明

### 邮箱配置

- `EMAIL_USERNAME`: 网易企业邮箱用户名
- `EMAIL_PASSWORD`: 邮箱密码或应用专用密码

### AI配置

- `DASHSCOPE_API_KEY`: 阿里云百炼平台API密钥
- `DASHSCOPE_BASE_URL`: API基础URL（默认为官方地址）
- `DASHSCOPE_APP_ID`: 百炼平台应用ID

### 日报配置

- `REPORT_RECIPIENTS`: 日报接收人邮箱列表（逗号分隔）
- `REPORT_FROM_EMAILS`: 需要收集日报的邮箱列表（逗号分隔）
- `REPORT_TIME`: 每天发送日报的时间（HH:MM格式）

## 日志管理

系统会在 `logs/` 目录下生成日志文件：

- `system_YYYY-MM-DD.log`: 系统运行日志
- `daily_report_YYYY-MM-DD.log`: 定时任务日志

日志会自动轮转，保留30天。

## 工作流程

1. **邮件收集**: 系统从指定邮箱收集包含关键词的日报邮件
2. **内容解析**: 解析邮件内容，提取纯文本信息
3. **AI汇总**: 调用OpenAI API对多份日报进行智能汇总
4. **邮件发送**: 将汇总后的日报发送给指定接收人
5. **日志记录**: 记录整个过程的详细日志

## 故障排除

### 邮件连接失败

1. 检查网易企业邮箱的IMAP/SMTP是否开启
2. 确认用户名和密码正确
3. 可能需要使用应用专用密码而非登录密码

### AI调用失败

1. 检查阿里云百炼平台API Key是否有效
2. 确认应用ID是否正确配置
3. 确认API额度是否充足
4. 检查网络连接是否正常

### 没有收集到日报

1. 确认邮箱中确实有符合条件的邮件
2. 检查发件人邮箱列表是否正确
3. 验证主题关键词是否匹配

## 扩展功能

系统支持以下扩展：

- 添加更多邮箱服务商支持
- 集成其他AI服务（如Azure OpenAI）
- 添加Web界面管理
- 支持更多报告格式（HTML、PDF等）
- 添加报告模板自定义

## 安全注意事项

- 邮箱密码和API Key需要妥善保管
- 建议使用应用专用密码而非主密码
- 定期更新依赖包以修复安全漏洞
- 生产环境建议使用更安全的配置管理方案

## 许可证

MIT License

## 技术支持

如有问题或建议，请提交Issue或联系开发者。 