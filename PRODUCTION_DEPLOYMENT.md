# POS系统生产环境部署指南

## 🚀 部署前准备

### 1. 系统要求
- Python 3.7+
- 至少 1GB RAM
- 至少 10GB 存储空间
- 稳定的网络连接

### 2. 安全要求
- 防火墙配置
- SSL证书
- 强密码策略
- 定期备份

## 📦 安装步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑环境变量
nano .env
```

**重要配置项：**
```bash
FLASK_ENV=production
SECRET_KEY=your-very-long-random-secret-key
SESSION_TIMEOUT=28800
```

### 3. 运行密码迁移
```bash
python migrate_passwords.py
```

### 4. 测试系统
```bash
python start_server.py
```

## 🔒 安全配置

### 1. 防火墙设置
```bash
# Ubuntu/Debian
sudo ufw allow 5000
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 2. SSL证书配置（推荐使用Nginx）
```bash
# 安装Nginx
sudo apt install nginx

# 配置Nginx反向代理
sudo nano /etc/nginx/sites-available/pos-system
```

Nginx配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 系统服务配置
创建systemd服务文件：
```bash
sudo nano /etc/systemd/system/pos-system.service
```

服务配置：
```ini
[Unit]
Description=POS System
After=network.target

[Service]
Type=simple
User=pos-user
WorkingDirectory=/path/to/pos-system
Environment=FLASK_ENV=production
ExecStart=/usr/bin/python3 start_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable pos-system
sudo systemctl start pos-system
```

## 🔄 备份策略

### 1. 自动备份脚本
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/pos-system"
DB_FILE="pos_system.db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp $DB_FILE $BACKUP_DIR/${DB_FILE}_${DATE}

# 保留最近30天的备份
find $BACKUP_DIR -name "${DB_FILE}_*" -mtime +30 -delete
```

### 2. 设置定时备份
```bash
# 编辑crontab
crontab -e

# 添加每日备份任务
0 2 * * * /path/to/backup.sh
```

## 📊 监控和维护

### 1. 日志监控
```bash
# 查看服务状态
sudo systemctl status pos-system

# 查看日志
sudo journalctl -u pos-system -f
```

### 2. 性能监控
- 监控CPU和内存使用
- 监控磁盘空间
- 监控网络连接

### 3. 定期维护
- 每周检查日志
- 每月更新系统
- 每季度安全审计

## 🚨 故障排除

### 常见问题

1. **服务无法启动**
   - 检查端口是否被占用
   - 检查权限设置
   - 查看错误日志

2. **数据库连接失败**
   - 检查数据库文件权限
   - 检查磁盘空间
   - 验证数据库完整性

3. **用户无法登录**
   - 检查密码迁移是否完成
   - 验证会话配置
   - 检查网络连接

## 📞 技术支持

如遇到问题，请检查：
1. 系统日志
2. 应用日志
3. 网络连接
4. 配置文件

## 🔐 安全建议

1. **定期更新密码**
2. **限制访问IP**
3. **启用审计日志**
4. **定期安全扫描**
5. **备份重要数据** 