# 项目结构说明

## 📁 目录结构

```
dailyreport/
├── 📄 核心程序文件
│   ├── web_app.py              # 主程序：Web应用 + 定时任务
│   ├── config.py               # 配置管理：环境变量解析和验证
│   ├── email_handler.py        # 邮件处理：IMAP收取 + SMTP发送
│   ├── email_formatter.py      # 邮件格式化：内容格式化和缩进
│   ├── ai_summarizer.py        # AI汇总：两阶段处理架构
│   ├── report_system.py        # 日报系统：业务逻辑封装
│   └── scheduler.py            # 定时任务：独立调度器（可选）
│
├── 🌐 前端资源
│   ├── templates/              # HTML模板
│   │   ├── base.html          # 基础模板
│   │   ├── index.html         # 主页面
│   │   └── history.html       # 历史记录页面
│   └── static/                # 静态资源
│       ├── css/
│       │   └── style.css      # 自定义样式
│       └── js/                # JavaScript文件（本地）
│
├── 💾 数据存储
│   ├── daily_reports.db       # SQLite数据库
│   └── logs/                  # 日志文件
│       └── system_*.log       # 按日期分割的日志
│
├── ⚙️ 配置文件
│   ├── .env                   # 环境变量配置（需创建）
│   ├── env.example            # 环境变量模板
│   ├── create_env.py          # 环境配置脚本
│   ├── requirements.txt       # Python依赖包
│   └── .gitignore            # Git忽略文件
│
├── 🔧 部署文件
│   └── daily-report.service   # systemd服务配置
│
└── 📖 文档文件
    ├── README.md              # 主要文档（整合版）
    └── PROJECT_STRUCTURE.md   # 项目结构说明（本文件）
```

## 📋 文件说明

### 核心程序文件

#### `web_app.py` - 主程序
- **功能**: Flask Web应用 + 后台定时任务
- **特点**: 
  - 集成了Web界面和定时任务
  - 支持热更新开发模式
  - 提供完整的API接口
  - 实时状态监控

#### `config.py` - 配置管理
- **功能**: 环境变量解析和配置验证
- **特点**:
  - 使用Pydantic进行类型验证
  - 支持默认值和必需参数
  - 配置分组管理（邮箱、AI、系统）

#### `email_handler.py` - 邮件处理
- **功能**: IMAP邮件收取和SMTP邮件发送
- **特点**:
  - 支持多种邮箱服务商
  - 智能邮件筛选和解析
  - HTML/纯文本格式处理

#### `email_formatter.py` - 邮件格式化
- **功能**: 邮件内容格式化和美化
- **特点**:
  - 专业的邮件格式
  - 缩进层次清晰
  - 支持多种内容类型

#### `ai_summarizer.py` - AI汇总
- **功能**: 两阶段AI处理架构
- **特点**:
  - 个人日报预处理
  - 团队内容整合
  - 阿里云百炼平台集成

#### `report_system.py` - 日报系统
- **功能**: 业务逻辑封装
- **特点**:
  - 完整的日报生成流程
  - 错误处理和重试机制
  - 日志记录和监控

#### `scheduler.py` - 定时任务（可选）
- **功能**: 独立的定时任务调度器
- **特点**:
  - 随机时间生成
  - 任务状态跟踪
  - 可独立运行

### 前端资源

#### `templates/` - HTML模板
- **base.html**: 基础模板，包含公共布局
- **index.html**: 主页面，Markdown编辑器和功能面板
- **history.html**: 历史记录页面，数据展示和搜索

#### `static/` - 静态资源
- **css/style.css**: 自定义样式，优化界面体验
- **js/**: 本地JavaScript文件，避免CDN依赖

### 数据存储

#### `daily_reports.db` - SQLite数据库
- **表结构**:
  - `user_content`: 用户输入内容
  - `generated_reports`: 生成的日报
  - `scheduler_logs`: 定时任务日志

#### `logs/` - 日志系统
- **文件格式**: `system_YYYY-MM-DD.log`
- **内容**: 详细的操作日志和错误信息
- **管理**: 自动轮转，保留30天

### 配置文件

#### `.env` - 环境变量（需创建）
```env
# 邮箱配置
EMAIL_ADDRESS=your-email@domain.com
EMAIL_PASSWORD=your-password
IMAP_SERVER=imap.domain.com
SMTP_SERVER=smtp.domain.com

# AI配置
DASHSCOPE_API_KEY=your-api-key
DASHSCOPE_APP_ID=your-app-id

# 系统配置
TARGET_SENDERS=user1@domain.com,user2@domain.com
SUBJECT_KEYWORDS=日报
```

#### `requirements.txt` - Python依赖
```
Flask==3.0.0
APScheduler==3.10.4
dashscope==1.14.1
pydantic==2.5.2
python-dotenv==1.0.0
beautifulsoup4==4.12.2
```

## 🚀 启动方式

### 开发模式
```bash
python web_app.py
```
- 自动热更新
- 详细日志输出
- 调试模式开启

### 生产模式
```bash
# 使用systemd服务
sudo systemctl start daily-report

# 或直接运行（后台）
nohup python web_app.py > /dev/null 2>&1 &
```

## 🔄 工作流程

1. **Web界面编辑** → 用户输入工作内容
2. **内容保存** → 存储到SQLite数据库
3. **邮件收集** → IMAP收取团队日报邮件
4. **AI处理** → 两阶段智能汇总
5. **格式化** → 生成专业邮件格式
6. **发送邮件** → SMTP发送给指定接收人
7. **历史记录** → 保存完整处理记录

## 🔧 扩展点

### 添加新功能
1. 在 `web_app.py` 中添加新路由
2. 创建对应的HTML模板
3. 更新CSS和JavaScript
4. 编写测试用例

### 集成新服务
1. 创建新的处理模块
2. 在 `config.py` 中添加配置
3. 更新 `requirements.txt`
4. 修改主程序调用

### 数据库扩展
1. 在 `web_app.py` 中添加新表
2. 更新数据模型
3. 编写迁移脚本
4. 更新API接口

## 📊 监控指标

### 系统健康
- Web应用响应时间
- 定时任务执行状态
- 数据库连接状态
- 磁盘空间使用

### 业务指标
- 日报生成成功率
- 邮件发送成功率
- AI处理响应时间
- 用户活跃度

### 日志监控
```bash
# 实时查看日志
tail -f logs/system_$(date +%Y-%m-%d).log

# 错误日志统计
grep "ERROR" logs/*.log | wc -l

# 任务执行统计
grep "定时任务执行" logs/*.log
```

## 🛠️ 维护建议

### 定期维护
- 每周检查日志文件大小
- 每月清理过期数据
- 每季度更新依赖包
- 定期备份数据库

### 性能优化
- 监控数据库查询性能
- 优化AI调用频率
- 压缩静态资源
- 启用浏览器缓存

### 安全加固
- 定期更换API密钥
- 检查文件权限设置
- 监控异常访问
- 更新安全补丁 