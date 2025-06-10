# 第五人格皮肤首字母查询系统

**版本**: v1.0.0

一个基于 Flask 的第五人格皮肤首字母查询工具，支持拼音搜索和管理仪表板功能。

## 🌟 功能特性

- **智能拼音查询**: 支持皮肤名称的拼音首字母快速查询
- **管理仪表板**: 提供用户请求统计和数据分析
- **请求日志**: 完整记录用户查询历史和系统运行状态
- **响应式设计**: 使用 Tailwind CSS 构建的现代化用户界面
- **生产就绪**: 支持 Gunicorn 生产环境部署
- **配置灵活**: 支持多环境配置和外部配置文件

## 🛠️ 技术栈

- **后端框架**: Flask 2.0+ (使用应用工厂模式)
- **数据库**: SQLite 3 (带连接池优化)
- **WSGI服务器**: Gunicorn (生产环境)
- **前端框架**: Tailwind CSS
- **中文处理**: pypinyin
- **HTTP客户端**: requests
- **HTML解析**: BeautifulSoup4
- **静态文件**: WhiteNoise
- **配置管理**: TOML

## 📁 项目结构

```
d5collect/
├── app/                    # Flask 应用主目录
│   ├── __init__.py        # 应用工厂和配置
│   ├── routes/            # 路由模块
│   │   └── main.py        # 主要路由处理
│   └── templates/         # Jinja2 模板
│       └── index.html     # 主页模板
├── database/              # 数据库相关
│   └── models.py          # 数据库模型和连接池
├── logs/                  # 日志文件目录
├── config.py              # 配置类定义
├── dashboard.py           # 仪表板功能
├── run.py                 # 应用启动入口
├── requirements.txt       # Python 依赖
├── main_config_template.toml  # 配置模板
└── README.md              # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- pip

### 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd d5collect

# 创建虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置设置

1. **复制配置模板**:
```bash
cp main_config_template.toml main_config.toml
```

2. **编辑配置文件** (`main_config.toml`):
```toml
[dashboard]
username = "your_username"    # 仪表板登录用户名
password = "your_password"    # 仪表板登录密码
```

### 开发环境运行

```bash
# 直接运行
python run.py

# 或使用 Flask 开发服务器
set FLASK_APP=run.py
set FLASK_ENV=development
flask run
```

应用将在 `http://localhost:9877` 启动。

## 🔧 配置说明

### 环境配置

项目支持多环境配置，通过 `FLASK_ENV` 环境变量控制：

- `development`: 开发环境 (默认)
- `production`: 生产环境
- `testing`: 测试环境

### 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Flask 密钥 | 随机生成 |
| `DATABASE_FILE` | SQLite 数据库文件路径 | `database/app.db` |
| `LOG_DIR` | 日志文件目录 | `logs` |
| `HOST` | 服务器主机 | `0.0.0.0` |
| `PORT` | 服务器端口 | `9877` |

## 📊 API 文档

### 主要端点

#### 1. 主页查询
- **URL**: `/`
- **方法**: `GET`, `POST`
- **功能**: 皮肤首字母查询
- **参数**: 
  - `text` (POST): 查询文本

#### 2. 仪表板
- **URL**: `/dashboard`
- **方法**: `GET`
- **功能**: 管理仪表板主页
- **认证**: 需要登录

#### 3. 仪表板登录
- **URL**: `/dashboard/login`
- **方法**: `GET`, `POST`
- **功能**: 仪表板用户认证

#### 4. 仪表板登出
- **URL**: `/dashboard/logout`
- **方法**: `POST`
- **功能**: 用户登出

## 🚀 生产部署

### 使用 Gunicorn

项目提供了专门的 Gunicorn 配置文件 `deployment/gunicorn_config.py`，推荐使用配置文件启动：

```bash
# 使用配置文件启动 (推荐)
gunicorn -c deployment/gunicorn_config.py run:app

# 基本启动
gunicorn -w 4 -b 0.0.0.0:9876 run:app

# 手动配置启动
gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:9876 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info \
  run:app
```

应用将在 `http://localhost:9876` 启动。

### Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:9876;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 禁用缓冲以提高响应速度
        proxy_buffering off;
        
        # 忽略客户端中断
        proxy_ignore_client_abort on;
    }
    
    # 静态文件处理
    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Systemd 服务配置

创建 `/etc/systemd/system/d5collect.service`:

```ini
[Unit]
Description=D5 Collect Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/d5collect
Environment="PATH=/path/to/d5collect/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/path/to/d5collect/venv/bin/gunicorn -c deployment/gunicorn_config.py run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable d5collect
sudo systemctl start d5collect
```

## 🗄️ 数据库

### 数据库结构

项目使用 SQLite 数据库，主要表结构：

```sql
CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_input TEXT,
    search_results TEXT,
    ip_address TEXT
);

CREATE INDEX idx_requests_timestamp ON requests(timestamp);
CREATE INDEX idx_requests_ip ON requests(ip_address);
```

### 数据库连接池

项目实现了 SQLite 连接池以提高性能：
- 最大连接数: 10
- 连接超时: 30秒
- 自动重试机制

## 📝 日志系统

### 日志配置

- **日志级别**: INFO (生产环境), DEBUG (开发环境)
- **日志格式**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **日志轮转**: 按大小轮转 (10MB)
- **保留文件**: 5个备份文件

### 日志文件

- `logs/app.log`: 应用主日志
- `logs/access.log`: 访问日志 (Gunicorn)
- `logs/error.log`: 错误日志 (Gunicorn)

## 🔍 故障排除

### 常见问题

1. **数据库锁定错误**
   ```
   解决方案: 检查数据库文件权限，确保应用有读写权限
   ```

2. **端口占用**
   ```bash
   # 查找占用端口的进程
   netstat -ano | findstr :5000
   # 终止进程
   taskkill /PID <PID> /F
   ```

3. **依赖安装失败**
   ```bash
   # 升级 pip
   python -m pip install --upgrade pip
   # 清除缓存重新安装
   pip install --no-cache-dir -r requirements.txt
   ```

4. **配置文件未找到**
   ```
   确保 main_config.toml 文件存在于项目根目录
   检查文件权限和格式
   ```

### 性能优化

1. **数据库优化**
   - 定期清理旧日志数据
   - 优化查询索引
   - 使用连接池

2. **应用优化**
   - 启用 Gzip 压缩
   - 配置静态文件缓存
   - 使用 CDN 加速

3. **服务器优化**
   - 调整 Gunicorn worker 数量
   - 配置适当的超时时间
   - 监控内存使用情况

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看 [故障排除](#-故障排除) 部分
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 Issue 描述问题

---

**注意**: 本项目仅供学习和研究使用，请遵守相关法律法规。