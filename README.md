# D5Collect - 谐音字皮肤查询工具

## 项目简介

D5Collect是一个基于Flask的Web应用，专为第五人格游戏玩家设计，可以根据输入的汉字或字母，查找与之发音相似的游戏角色皮肤。该工具利用拼音匹配原理，帮助玩家快速找到谐音字开头的皮肤，展示在收集页面中形成藏头的效果。

## 功能特点

- **谐音字匹配**：根据输入的文字，查找发音相似的游戏皮肤
- **精确匹配高亮**：完全匹配的结果会有特殊高亮显示
- **筛选功能**：支持按品质和角色筛选结果
- **响应式设计**：适配各种设备屏幕大小
- **直观的结果展示**：以图文并茂的方式展示匹配结果

## 安装说明

### 前提条件

- Python 3.6+
- pip (Python包管理工具)

### 安装步骤

1. 克隆或下载本项目到本地

2. 创建并激活虚拟环境（可选但推荐）
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

## 使用方法

1. 启动应用
   
   开发环境：
   ```bash
   python app.py
   ```
   
   生产环境（使用Gunicorn）：
   ```bash
   gunicorn -c gunicorn_config.py app:app
   ```
   或直接使用：
   ```bash
   gunicorn --workers=4 --bind=0.0.0.0:8000 app:app
   ```

2. 在浏览器中访问：
   - 开发环境：`http://127.0.0.1:5000/`
   - 生产环境：`http://127.0.0.1:9876/`

3. 在搜索框中输入想要查询的文字，点击"查找"按钮

4. 查看匹配结果，可以使用筛选功能按品质或角色筛选

## 数据说明

项目使用`costumes_data.json`文件存储皮肤数据，包含以下信息：
- 角色名称
- 皮肤名称
- 皮肤品质
- 皮肤图片URL
- Wiki链接

## 技术栈

- **后端**：Flask (Python Web框架)
- **拼音处理**：pypinyin (汉字转拼音库)
- **前端**：HTML, Tailwind CSS, JavaScript

## 依赖项

- Flask==2.0.1
- pypinyin==0.47.1
- gunicorn==23.0.0

## 贡献指南

欢迎提交问题报告和功能建议，也欢迎通过Pull Request贡献代码。

## 许可证

[MIT](https://opensource.org/licenses/MIT)