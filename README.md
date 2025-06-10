# D5Collect - 谐音字皮肤查询工具

D5Collect 是一个基于 Flask 开发的 Web 应用，专为《第五人格》游戏玩家设计。它能根据用户输入的汉字或字母，利用拼音匹配原理，快速查找具有相似发音首字的游戏皮肤，帮助玩家轻松实现“藏头诗”等创意皮肤搭配。

**在线体验**: [第五人格谐音字皮肤查询工具](https://d5collect.narakapve.com/)

## ✨ 功能特点

  * **核心功能 - 谐音匹配**: 输入任意句子，即可查找每个字对应的同音及谐音皮肤。
  * **精准高亮**: 在搜索结果中，与输入字完全匹配的皮肤将以黄色高亮突出显示。
  * **强大筛选**: 在客户端动态按**品质**和**角色**进行多重筛选，无需刷新页面。
  * **统计后台 (Dashboard)**: 内置一个受密码保护的统计后台，通过图表和列表展示网站的详细使用情况，如总请求数、独立访客趋势、热门IP等。
  * **动态刷新与动画**: Dashboard 页面支持每3秒自动刷新和手动刷新，并配有平滑的数字增长及列表项更新动画。
  * **自动化数据更新**: 提供了独立的 Python 脚本 (`scripts/update_data.py`)，可一键从 Bilibili Wiki 抓取最新的皮肤数据。
  * **现代化技术栈**: 采用 Flask 应用工厂模式构建，后端逻辑清晰，前端使用 Tailwind CSS 保证了界面的美观与响应式。
  * **高效数据库查询**: 所有皮肤数据预处理后存入 SQLite 数据库，并建立了拼音索引，确保了高效的搜索响应速度。

## 🛠️ 技术栈

  * **后端**: Flask, Gunicorn
  * **数据库**: SQLite
  * **拼音处理**: `pypinyin`
  * **数据抓取**: `requests`, `BeautifulSoup4`
  * **前端**: HTML5, Tailwind CSS, Chart.js, Luxon.js, Font Awesome, Vanilla JavaScript
  * **配置**: TOML

## 🏗️ 项目结构

```
d5collect/
├── run.py                    # 应用入口
├── app/                      # 主应用模块
│   ├── __init__.py           # Flask应用工厂
│   ├── config.py             # 环境配置
│   └── routes/               # 路由蓝图
│       ├── main.py           # 主站路由
│       └── dashboard.py      # Dashboard路由
├── database/                 # 数据库模块
│   ├── models.py             # 数据库模型与操作函数
│   └── migrations/           # 数据库迁移脚本
├── data/                     # 数据文件
│   └── costumes_data.json    # 原始皮肤数据
├── scripts/                  # 辅助脚本
│   └── update_data.py        # 数据更新脚本
├── deployment/               # 部署配置
│   └── gunicorn_config.py    # Gunicorn生产环境配置
├── templates/                # HTML模板
│   ├── index.html
│   ├── login.html
│   └── dashboard.html
├── requirements.txt          # Python依赖
└── main_config.toml          # (需手动创建)主配置文件
```

## 🚀 安装与启动

#### 1\. 克隆项目

```bash
git clone https://github.com/Wangnov/d5collect.git
cd d5collect
```

#### 2\. 创建并激活虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3\. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4\. 配置应用

应用需要一个主配置文件来设置 Dashboard 的登录凭据。您需要从模板文件复制一份。

```bash
# 从模板复制一份配置文件
cp main_config_template.toml main_config.toml
```

然后打开 `main_config.toml` 文件，**务必修改**默认的 `password`。

```toml
[dashboard]
username = "admin"
password = "your_strong_password_here"
```

#### 5\. 初始化数据库

首次运行时，需要创建并填充数据库。此脚本会读取 `data/costumes_data.json` 并将其载入 SQLite。

```bash
python database/migrations/migrate_costumes.py
```

#### 6\. 运行应用

  * **开发环境**:

    ```bash
    python run.py
    ```

    应用将在 `http://127.0.0.1:9877` 上运行。

  * **生产环境 (推荐)**:
    使用 Gunicorn 启动，它会读取 `deployment/gunicorn_config.py` 中的配置。

    ```bash
    gunicorn -c deployment/gunicorn_config.py run:app
    ```

    应用将在 `http://127.0.0.1:9876` 上运行。

  * **访问应用**:

      * 主站: `http://<your_ip>:<port>/`
      * 后台: `http://<your_ip>:<port>/dashboard`

## 📊 数据管理

本应用的数据流是独立的，以确保数据的准确性和时效性。

1.  **抓取新数据**:
    运行 `update_data.py` 脚本，它会从 BWIKI 抓取最新的皮肤数据并保存到 `costumes_data_updated.json`。

    ```bash
    python scripts/update_data.py
    ```

2.  **更新本地数据**:
    抓取完成后，用新生成的 `costumes_data_updated.json` 文件**覆盖**原有的 `data/costumes_data.json`。

3.  **同步到数据库**:
    再次运行数据库迁移脚本，将更新后的 JSON 数据同步到 SQLite 数据库中。

    ```bash
    python database/migrations/migrate_costumes.py
    ```

## 🤝 贡献

欢迎通过 Fork 和 Pull Request 的方式为本项目做出贡献。如果您发现了 Bug 或有任何建议，请随时提交 Issue。

## 📄 许可证

本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证。