# D5Collect - 谐音字皮肤查询工具

## 项目简介

D5Collect是一个基于Flask的Web应用，专为第五人格游戏玩家设计，可以根据输入的汉字或字母，查找与之发音相似的游戏角色皮肤。该工具利用拼音匹配原理，帮助玩家快速找到谐音字开头的皮肤，展示在收集页面中形成藏头的效果。

可在这里体验项目：[第五人格谐音字皮肤查询工具](https://d5collect.narakapve.com/)

## 功能特点

- **谐音字匹配**：根据输入的文字，查找发音相似的游戏皮肤
- **精确匹配高亮**：完全匹配的结果会有特殊高亮显示
- **筛选功能**：支持按品质和角色筛选结果
- **响应式设计**：适配各种设备屏幕大小
- **直观的结果展示**：以图文并茂的方式展示匹配结果
- **模块化架构**：采用Flask应用工厂模式，代码结构清晰
- **数据库支持**：使用SQLite存储搜索记录和统计信息

## 项目结构

```
d5collect/
├── run.py                    # 应用入口点
├── app/                      # 主应用模块
│   ├── __init__.py          # Flask应用工厂
│   ├── config.py            # 配置文件
│   └── routes/              # 路由模块
│       ├── __init__.py
│       └── main.py          # 主路由
├── database/                 # 数据库相关
│   ├── __init__.py
│   ├── models.py            # 数据库模型和操作
│   └── migrations/          # 数据库迁移脚本
│       └── migrate_costumes.py
├── data/                     # 数据文件
│   └── costumes_data.json   # 皮肤数据
├── scripts/                  # 工具脚本
│   ├── pinyin.py            # 拼音处理工具
│   └── update_data.py       # 数据更新脚本
├── deployment/               # 部署配置
│   └── gunicorn_config.py   # Gunicorn配置
├── templates/                # HTML模板
│   └── index.html
├── static/                   # 静态资源
├── logs/                     # 日志文件
├── requirements.txt          # Python依赖
└── README.md                # 项目说明
```

## 安装说明

### 前提条件

- Python 3.7+
- pip (Python包管理工具)

### 安装步骤

1. 克隆或下载本项目到本地

2. 创建并激活虚拟环境（推荐）
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或
   .venv\Scripts\activate  # Windows
   ```

3. 安装依赖包
   ```bash
   pip install -r requirements.txt
   ```

4. 初始化数据库（可选）
   ```bash
   python database/migrations/migrate_costumes.py
   ```

## 使用方法

### 开发环境

```bash
python run.py
```

### 生产环境

使用Gunicorn部署：
```bash
gunicorn -c deployment/gunicorn_config.py run:app
```

### 访问应用

在浏览器中访问：`http://127.0.0.1:9876/`

### 使用步骤

1. 在搜索框中输入想要查询的文字
2. 点击"查找"按钮
3. 查看匹配结果
4. 使用筛选功能按品质或角色筛选结果

## 数据管理

### 皮肤数据

项目使用`data/costumes_data.json`文件存储皮肤数据，包含：
- 角色名称
- 皮肤名称
- 皮肤品质
- 皮肤图片URL
- Wiki链接

### 数据库

使用SQLite数据库存储：
- 搜索记录
- 用户统计
- 系统日志

### 数据更新

使用脚本更新皮肤数据：
```bash
python scripts/update_data.py
```

## 技术栈

- **后端框架**：Flask 2.x
- **应用架构**：Flask应用工厂模式
- **数据库**：SQLite
- **拼音处理**：pypinyin
- **前端**：HTML5, Tailwind CSS, JavaScript
- **部署**：Gunicorn
- **数据抓取**：requests, beautifulsoup4

## 配置说明

应用支持多环境配置，在`app/config.py`中定义：

- **开发环境**：`DevelopmentConfig`
- **生产环境**：`ProductionConfig`
- **测试环境**：`TestingConfig`

通过环境变量`FLASK_ENV`控制配置选择。

## 开发指南

### 添加新路由

在`app/routes/`目录下创建新的路由模块，并在`app/routes/__init__.py`中注册。

### 数据库操作

所有数据库相关操作都在`database/models.py`中定义，使用连接池管理数据库连接。

### 日志记录

应用日志存储在`logs/`目录下，支持按日期轮转。

## 部署说明

### 生产环境部署

1. 设置环境变量：
   ```bash
   export FLASK_ENV=production
   ```

2. 使用Gunicorn启动：
   ```bash
   gunicorn -c deployment/gunicorn_config.py run:app
   ```

### Docker部署（可选）

项目支持Docker容器化部署，可根据需要创建Dockerfile。

## 贡献指南

1. Fork本项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建Pull Request

## 问题反馈

如遇到问题或有功能建议，请通过以下方式反馈：
- 提交Issue
- 发送邮件
- 在线反馈

## 许可证

本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证。

## 更新日志

### v2.0.0
- 重构项目结构，采用模块化设计
- 实现Flask应用工厂模式
- 添加数据库支持
- 优化配置管理
- 改进部署方式

### v1.0.0
- 初始版本发布
- 基础谐音字匹配功能
- Web界面实现