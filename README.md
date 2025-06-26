# 智能日报系统

一个功能完整的自动化日报管理系统，支持Web界面编辑、邮件自动收集、AI智能汇总和定时发送等功能。

# 主要功能
作为一个 leader，我每天要汇总大家的日报，然后再向上面 boss 汇报工作。这很繁琐。所以这个系统的主要功能就是自动收集团队成员每天的日报，然后结合自己的每天的日报，由 AI 进行内容美化，发给 boss。

## 🌟 系统特色

### 📱 Web界面管理
- **现代化界面**：基于Flask + Bootstrap 5的响应式Web界面
- **Markdown编辑器**：支持完整的Markdown语法，实时预览
- **智能模板**：提供工作、会议、项目、表格等快速模板
- **热更新支持**：开发模式下代码修改自动重载

### 📧 智能邮件处理
- **多邮箱支持**：支持网易企业邮箱等IMAP/SMTP协议
- **自动收集**：定时从指定邮箱收集团队日报邮件
- **智能筛选**：按发件人、主题关键词、时间范围筛选
- **格式解析**：自动解析HTML和纯文本邮件格式

### 🤖 AI智能汇总
- **两阶段处理**：先分别处理个人日报，再整体整合
- **阿里云百炼**：集成阿里云百炼平台，提供高质量AI汇总
- **内容优化**：智能去重、按项目分类、突出重点风险
- **格式美化**：生成专业的邮件格式，缩进层次清晰

### ⏰ 智能定时任务
- **随机时间**：每天21:00-22:00随机时间发送，避免机械化
- **精确到秒**：3600种可能的发送时间，真正的随机性
- **状态监控**：Web界面实时显示定时任务状态和执行历史
- **手动控制**：支持手动启动/停止定时任务

### 💾 数据管理
- **SQLite存储**：轻量级数据库，无需额外配置
- **历史记录**：完整保存所有生成的日报，支持查看和重发
- **内容备份**：用户输入自动保存，防止数据丢失
- **日志系统**：详细的操作日志，便于问题排查

## 🏗️ 系统架构

```
智能日报系统
├── 🌐 Web应用层 (web_app.py)
│   ├── Flask路由和API
│   ├── 前端界面管理
│   ├── 用户交互处理
│   └── 定时任务监控
├── 📧 邮件处理层 (email_handler.py)
│   ├── IMAP邮件收取
│   ├── SMTP邮件发送
│   └── 邮件格式化 (email_formatter.py)
├── 🤖 AI处理层 (ai_summarizer.py)
│   ├── 个人日报处理
│   ├── 团队日报整合
│   └── 内容智能汇总
├── ⏰ 定时任务层 (scheduler.py)
│   ├── 随机时间生成
│   ├── 任务调度管理
│   └── 执行状态跟踪
├── ⚙️ 配置管理层 (config.py)
│   ├── 环境变量管理
│   ├── 参数验证
│   └── 默认值设置
└── 💾 数据存储层
    ├── SQLite数据库
    ├── 日志文件系统
    └── 静态资源管理
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 企业邮箱账号（支持IMAP/SMTP）
- 阿里云百炼平台账号

### 一键安装

1. **克隆项目**
```bash
git clone <项目地址>
cd dailyreport
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 复制配置模板
cp env.example .env

# 或使用配置脚本
python create_env.py
```

4. **启动系统**
```bash
# 推荐：使用快速启动脚本（自动检查环境）
python start.py

# 或直接启动主程序
python web_app.py
```

5. **访问界面**
打开浏览器访问：http://localhost:5002

### 环境配置

编辑 `.env` 文件：

```env
# 邮箱配置（必需）
EMAIL_ADDRESS=mail@mailbox.com
EMAIL_PASSWORD=your-password
IMAP_SERVER=imap.mailbox.com
IMAP_PORT=993
SMTP_SERVER=smtp.mailbox.com
SMTP_PORT=465

# AI配置（必需）
DASHSCOPE_API_KEY=sk-your-api-key
DASHSCOPE_APP_ID=your-app-id

# 日报收集配置
TARGET_SENDERS=teammate@mailbox.com
SUBJECT_KEYWORDS=日报
REPORT_RECIPIENTS=boss@company.com

# 系统配置（可选）
LOG_LEVEL=INFO
DATABASE_PATH=daily_reports.db
```

## 📖 使用指南

### Web界面使用

#### 1. 编写个人工作内容
- 在左侧编辑区输入工作内容
- 支持完整Markdown语法
- 使用右侧快速模板提高效率

#### 2. 保存和生成
- 点击"保存内容"保存到数据库
- 点击"生成日报"开始AI汇总
- 系统自动收集邮件并整合

#### 3. 查看和管理
- 实时预览生成的日报
- 查看历史记录和统计
- 监控定时任务状态

### 快速模板

系统提供四种常用模板：

#### 工作模板
```markdown
## 今日工作总结

### ✅ 已完成工作
- 

### 🔄 进行中工作
- 

### 📋 明日计划
- 

### 💡 其他说明
- 
```

#### 会议模板
```markdown
## 会议记录 - {当前日期}

**会议主题：** 
**参与人员：** 
**会议时间：** 

### 📋 会议议题
1. 

### ✅ 决定事项
1. 

### 📝 行动计划
1. 
```

#### 项目模板
```markdown
## 项目进展汇报

**项目名称：** 
**汇报日期：** {当前日期}

### 📊 项目概况
- **当前阶段：** 
- **完成进度：** 
- **预计完成：** 

### ✅ 本周完成
- 

### 🔄 下周计划
- 

### ⚠️ 风险提示
- 
```
### 定时任务管理

#### 智能随机发送
- 每天21:00-22:00之间随机时间发送
- 精确到秒级，共3600种可能时间
- 避免机械化，更加人性化

#### 状态监控
- 实时显示定时任务运行状态
- 查看下次执行时间
- 历史执行记录和结果

#### 手动控制
- Web界面一键启动/停止
- 立即执行测试功能
- 任务状态实时更新

## 🔧 高级配置

### 邮箱服务器配置

不同邮箱服务商的配置示例：

#### 网易企业邮箱
```env
IMAP_SERVER=imap.163.com
IMAP_PORT=993
SMTP_SERVER=smtp.163.com
SMTP_PORT=465
```

#### 自定义企业邮箱
```env
IMAP_SERVER=imap.your-domain.com
IMAP_PORT=993
SMTP_SERVER=smtp.your-domain.com
SMTP_PORT=465
```

### AI配置优化

#### 阿里云百炼平台
1. 登录阿里云百炼控制台
2. 创建应用获取App ID
3. 生成API Key
4. 配置到环境变量

#### 提示词自定义
系统支持自定义AI提示词，可在 `ai_summarizer.py` 中修改：
- 个人日报处理提示词
- 团队汇总整合提示词
- 输出格式要求

### 数据库管理

#### 数据备份
```bash
# 备份数据库
cp daily_reports.db daily_reports_backup.db

# 查看数据库内容
sqlite3 daily_reports.db
.tables
.schema user_content
```

#### 数据清理
```sql
-- 删除30天前的记录
DELETE FROM generated_reports 
WHERE created_at < datetime('now', '-30 days');

-- 清理无效的用户内容
DELETE FROM user_content 
WHERE content IS NULL OR content = '';
```

## 📊 系统监控

### 日志系统

系统提供详细的日志记录：

#### 日志级别
- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息记录
- `WARNING`: 警告信息
- `ERROR`: 错误信息

#### 日志文件
```
logs/
├── web_app.log          # Web应用日志
├── scheduler.log        # 定时任务日志
├── email_handler.log    # 邮件处理日志
└── ai_summarizer.log    # AI处理日志
```

#### 日志配置
```env
LOG_LEVEL=INFO
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5
```

### 性能监控

#### 系统指标
- 邮件收集成功率
- AI处理响应时间
- 定时任务执行状态
- 数据库查询性能

#### 监控方法
```python
# 在Web界面查看
/scheduler_status  # 定时任务状态
/api/history      # 历史记录统计

# 命令行查看
tail -f logs/web_app.log
```

## 🚨 故障排除

### 常见问题及解决方案

#### 1. 邮箱连接失败
**问题现象**：无法收取或发送邮件

**解决方案**：
- 检查邮箱服务器地址和端口
- 确认邮箱密码正确
- 开启邮箱的IMAP/SMTP服务
- 使用应用专用密码（如果支持）

#### 2. AI调用失败
**问题现象**：日报生成失败或内容异常

**解决方案**：
- 检查API Key和App ID配置
- 确认网络连接正常
- 查看API配额是否充足
- 检查提示词长度是否超限

#### 3. 定时任务异常
**问题现象**：定时任务不执行或执行失败

**解决方案**：
- 查看定时任务状态页面
- 检查系统时间是否正确
- 确认Python进程正常运行
- 查看scheduler.log日志文件

#### 4. Web界面异常
**问题现象**：页面加载失败或功能异常

**解决方案**：
- 检查Flask应用是否正常启动
- 确认端口5002未被占用
- 清除浏览器缓存
- 检查static文件是否完整

#### 5. 数据库问题
**问题现象**：数据保存失败或查询异常

**解决方案**：
- 检查数据库文件权限
- 确认磁盘空间充足
- 备份并重建数据库
- 检查SQLite版本兼容性

### 调试技巧

#### 1. 开启详细日志
```env
LOG_LEVEL=DEBUG
```

#### 2. 测试邮件连接
```python
from email_handler import EmailHandler
from config import Config

config = Config()
handler = EmailHandler(config.email)
success = handler.test_connection()
print(f"邮件连接测试: {'成功' if success else '失败'}")
```

#### 3. 测试AI功能
```python
from ai_summarizer import AISummarizer
from config import Config

config = Config()
ai = AISummarizer(config.ai)
result = ai.test_connection()
print(f"AI连接测试: {'成功' if result else '失败'}")
```

#### 4. 手动执行任务
```python
from report_system import ReportSystem

system = ReportSystem()
system.run_daily_task()
```

## 🔒 安全建议

### 配置安全
- 使用环境变量存储敏感信息
- 定期更换API密钥和邮箱密码
- 限制系统访问权限
- 定期备份重要数据

### 网络安全
- 使用HTTPS访问（生产环境）
- 配置防火墙规则
- 监控异常访问
- 定期更新依赖包

### 数据安全
- 加密存储敏感数据
- 定期清理过期日志
- 控制数据访问权限
- 建立数据恢复机制

## 🚀 部署指南

### 开发环境
```bash
# 启用热更新
python web_app.py
```

### 生产环境

#### 使用systemd服务
```bash
# 复制服务文件
sudo cp daily-report.service /etc/systemd/system/

# 启用并启动服务
sudo systemctl enable daily-report
sudo systemctl start daily-report

# 查看服务状态
sudo systemctl status daily-report
```

#### 使用Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5002

CMD ["python", "web_app.py"]
```

#### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📈 扩展开发

### 添加新功能
1. 创建新的模块文件
2. 在web_app.py中添加路由
3. 更新前端界面
4. 编写测试用例

### 集成其他服务
- 钉钉、企业微信机器人
- 其他AI服务（GPT、Claude等）
- 数据可视化组件
- 移动端应用

### API扩展
系统支持RESTful API扩展：
```python
@app.route('/api/reports', methods=['GET'])
def get_reports():
    # 获取日报列表
    pass

@app.route('/api/reports', methods=['POST'])
def create_report():
    # 创建新日报
    pass
```

## 📝 更新日志

### v2.0.0 (2025-01-23)
- ✨ 新增Web界面管理
- 🤖 升级AI两阶段处理架构
- ⏰ 实现智能随机定时发送
- 🔥 支持热更新开发模式
- 📧 优化邮件格式化和缩进
- 💾 完善数据库和日志系统

### v1.0.0 (2024-12-20)
- 🎉 初始版本发布
- 📧 基础邮件收发功能
- 🤖 AI汇总功能
- ⏰ 定时任务支持

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. Fork项目到您的GitHub
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 技术支持

- 🐛 Bug报告：提交GitHub Issue
- 💡 功能建议：提交Feature Request
- 📧 邮件联系：[您的邮箱]
- 📖 文档wiki：[项目Wiki地址]

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！ 