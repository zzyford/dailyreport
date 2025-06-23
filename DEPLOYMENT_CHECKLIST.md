# 🚀 部署检查清单

## 📋 部署前检查

### ✅ 环境准备
- [ ] Python 3.8+ 已安装
- [ ] pip 包管理器可用
- [ ] 网络连接正常
- [ ] 磁盘空间充足（至少1GB）

### ✅ 项目文件
- [ ] 所有核心文件完整
  - [ ] `web_app.py` - 主程序
  - [ ] `config.py` - 配置管理
  - [ ] `email_handler.py` - 邮件处理
  - [ ] `email_formatter.py` - 邮件格式化
  - [ ] `ai_summarizer.py` - AI汇总
  - [ ] `report_system.py` - 日报系统
  - [ ] `scheduler.py` - 定时任务
- [ ] 前端资源完整
  - [ ] `templates/` 目录及HTML文件
  - [ ] `static/` 目录及CSS/JS文件
- [ ] 配置文件准备
  - [ ] `requirements.txt` - 依赖列表
  - [ ] `env.example` - 配置模板
  - [ ] `.gitignore` - Git忽略文件

### ✅ 依赖安装
```bash
# 安装Python依赖
pip install -r requirements.txt

# 验证关键包
python -c "import flask, apscheduler, dashscope, pydantic"
```

### ✅ 配置设置
- [ ] 复制配置模板：`cp env.example .env`
- [ ] 配置邮箱信息
  - [ ] `EMAIL_ADDRESS` - 邮箱地址
  - [ ] `EMAIL_PASSWORD` - 邮箱密码
  - [ ] `IMAP_SERVER` - IMAP服务器
  - [ ] `SMTP_SERVER` - SMTP服务器
- [ ] 配置AI服务
  - [ ] `DASHSCOPE_API_KEY` - API密钥
  - [ ] `DASHSCOPE_APP_ID` - 应用ID
- [ ] 配置日报设置
  - [ ] `TARGET_SENDERS` - 目标发件人
  - [ ] `SUBJECT_KEYWORDS` - 主题关键词
  - [ ] `REPORT_RECIPIENTS` - 接收人列表

## 🧪 功能测试

### ✅ 连接测试
```bash
# 使用快速启动脚本测试
python start.py

# 或直接启动主程序
python web_app.py
```

### ✅ Web界面测试
- [ ] 访问 http://localhost:5002
- [ ] 页面正常加载
- [ ] Markdown编辑器工作正常
- [ ] 模板插入功能正常
- [ ] 保存内容功能正常

### ✅ 邮件功能测试
- [ ] 邮箱连接成功
- [ ] 能够收取邮件
- [ ] 能够发送邮件
- [ ] 邮件格式正确

### ✅ AI功能测试
- [ ] AI服务连接成功
- [ ] 能够处理个人日报
- [ ] 能够整合团队内容
- [ ] 生成格式正确

### ✅ 定时任务测试
- [ ] 定时任务启动成功
- [ ] 状态页面显示正常
- [ ] 能够手动执行
- [ ] 随机时间生成正常

## 🏭 生产环境部署

### ✅ 系统服务配置
```bash
# 复制服务文件
sudo cp daily-report.service /etc/systemd/system/

# 修改服务文件中的路径
sudo vim /etc/systemd/system/daily-report.service

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable daily-report

# 启动服务
sudo systemctl start daily-report

# 检查状态
sudo systemctl status daily-report
```

### ✅ 防火墙配置
```bash
# 开放端口（如果需要外部访问）
sudo ufw allow 5002/tcp

# 或使用iptables
sudo iptables -A INPUT -p tcp --dport 5002 -j ACCEPT
```

### ✅ 反向代理配置（可选）
```nginx
# Nginx配置示例
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 📊 监控配置

### ✅ 日志监控
```bash
# 查看系统日志
sudo journalctl -u daily-report -f

# 查看应用日志
tail -f logs/system_$(date +%Y-%m-%d).log

# 设置日志轮转
sudo logrotate -f /etc/logrotate.d/daily-report
```

### ✅ 性能监控
- [ ] 设置CPU/内存监控
- [ ] 设置磁盘空间监控
- [ ] 设置网络连接监控
- [ ] 设置应用响应时间监控

### ✅ 告警配置
- [ ] 邮件发送失败告警
- [ ] AI服务异常告警
- [ ] 定时任务失败告警
- [ ] 系统资源异常告警

## 🔒 安全加固

### ✅ 文件权限
```bash
# 设置合适的文件权限
chmod 600 .env
chmod 644 *.py
chmod 755 start.py
chmod -R 755 static/
chmod -R 644 templates/
```

### ✅ 网络安全
- [ ] 限制访问IP（如果需要）
- [ ] 使用HTTPS（生产环境）
- [ ] 设置访问日志
- [ ] 配置防火墙规则

### ✅ 数据安全
- [ ] 定期备份数据库
- [ ] 加密敏感配置
- [ ] 设置访问控制
- [ ] 定期更新密钥

## 🔄 维护计划

### ✅ 日常维护
- [ ] 每日检查系统状态
- [ ] 每日检查日志文件
- [ ] 每周清理过期日志
- [ ] 每周备份数据库

### ✅ 定期维护
- [ ] 每月更新依赖包
- [ ] 每月检查安全补丁
- [ ] 每季度性能优化
- [ ] 每年密钥轮换

### ✅ 应急预案
- [ ] 服务异常处理流程
- [ ] 数据恢复流程
- [ ] 联系人和责任人
- [ ] 备用方案准备


✅ **部署完成标志**: 所有检查项都已完成，系统运行正常，监控告警配置完成。 