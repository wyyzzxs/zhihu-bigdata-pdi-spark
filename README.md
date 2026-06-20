# 知乎用户大数据分析与可视化平台

本项目为《大数据与云计算综合设计》课程设计项目，围绕知乎用户数据完成从数据采集结果清洗、云端数据库入库、PySpark 分布式统计分析，到 Flask + ECharts 前端可视化展示的完整流程。
项目使用 Kettle/PDI 将 JSON 数据清洗后写入云端 MySQL，再通过 PySpark 从 MySQL 中读取数据并生成统计结果，最终使用 Flask 提供 Web 服务，结合 ECharts 展示用户画像、内容贡献分布、高活跃用户排行、姓氏词云等分析结果。

## 一、项目功能

本系统主要实现以下功能：
1. 使用 Kettle/PDI 对原始 JSON 用户数据进行字段抽取、清洗和格式转换。
2. 将清洗后的知乎用户数据写入云端 MySQL 数据库。
3. 使用 PySpark 从 MySQL 中读取数据并进行统计分析。
4. 生成用户回答数分布、文章数分布、性别比例等基础统计结果。
5. 对中文昵称进行姓氏识别，支持常见复姓，并过滤非姓氏字符，生成清洗后的姓氏词云。
6. 新增 Top10 高回答用户统计，用于识别高活跃用户。
7. 新增回答数与文章数关系散点图，用于观察用户问答贡献与文章创作之间的关系。
8. 使用 Flask + ECharts 搭建数据可视化大屏。
9. 使用 Gunicorn + Nginx 部署 Web 服务，实现公网访问。

## 二、技术栈

| 模块 | 技术 |
|---|---|
| 数据清洗与入库 | Kettle / Pentaho Data Integration |
| 数据库 | MySQL |
| 分布式计算 | PySpark |
| 后端服务 | Flask |
| 可视化 | ECharts |
| 词云生成 | wordcloud |
| Web 部署 | Gunicorn + Nginx |
| 代码管理 | Git / GitHub |

## 三、项目结构

```text
zhihu-bigdata-pdi-spark/
├── README.md
├── requirements.txt
├── run_all_spark_jobs.sh
├── .env.example
├── .gitignore
├── sql/
│   └── 01_create_tables.sql
├── spark_jobs/
│   ├── common.py
│   ├── 01_overview.py
│   ├── 02_articles_hist.py
│   ├── 03_answers_hist.py
│   ├── 04_gender_pie.py
│   ├── 05_surname_wordcloud.py
│   ├── 06_top_users.py
│   └── 07_answer_article_scatter.py
└── webapp/
    ├── app.py
    └── static/
        ├── data/
        │   ├── overview.json
        │   ├── articles_hist.json
        │   ├── answers_hist.json
        │   ├── gender_pie.json
        │   ├── surname_wordcloud.json
        │   ├── top_users.json
        │   └── answer_article_scatter.json
        ├── img/
        │   └── surname_wordcloud.png
        └── js/
            └── echarts.min.js
````

## 四、数据表设计

项目核心数据表为 `zhihu_user`，主要字段如下：

| 字段名             | 含义     |
| --------------- | ------ |
| id              | 自增主键   |
| url_token       | 用户唯一标识 |
| name            | 用户昵称   |
| gender          | 性别编码   |
| gender_label    | 性别文本   |
| answer_count    | 回答数量   |
| articles_count  | 文章数量   |
| follower_count  | 粉丝数量   |
| following_count | 关注数量   |
| headline        | 用户简介   |

建表 SQL 位于：

```text
sql/01_create_tables.sql
```

## 五、数据处理流程

整体流程如下：

```text
原始 JSON 数据
    ↓
Kettle/PDI 字段解析、清洗、转换
    ↓
写入云端 MySQL 数据库
    ↓
PySpark 读取 MySQL 数据
    ↓
生成统计 JSON 与词云图片
    ↓
Flask 提供接口与页面
    ↓
ECharts 前端可视化展示
```

## 六、PySpark 统计任务

项目包含多个 PySpark 统计脚本：

| 脚本                             | 功能                          |
| ------------------------------ | --------------------------- |
| `01_overview.py`               | 统计用户总数、平均回答数、平均文章数、最大值等概览指标 |
| `02_articles_hist.py`          | 统计文章数分布直方图                  |
| `03_answers_hist.py`           | 统计回答数分布直方图                  |
| `04_gender_pie.py`             | 统计性别比例                      |
| `05_surname_wordcloud.py`      | 统计中文姓氏词云，支持复姓识别和非姓氏过滤       |
| `06_top_users.py`              | 统计 Top10 高回答用户              |
| `07_answer_article_scatter.py` | 生成回答数与文章数关系散点图数据            |

一键运行全部统计任务：

```bash
./run_all_spark_jobs.sh
```

运行完成后会在 `webapp/static/data/` 和 `webapp/static/img/` 下生成统计结果。

## 七、可视化展示内容

前端页面主要包含以下模块：

1. KPI 指标卡片
   展示用户总数、平均回答数、平均文章数、最高回答数、最高文章数等核心指标。
2. 回答数分布直方图
   展示不同回答数量区间内的用户数量，用于分析用户问答活跃度分布。
3. 文章数分布直方图
   展示不同文章数量区间内的用户数量，用于分析用户创作活跃度分布。
4. 性别比例环形图
   展示用户性别结构，作为用户画像的基础维度。
5. Top10 高回答用户排行
   展示回答数最高的用户，用于识别平台中的高活跃用户。
6. 回答数与文章数关系散点图
   展示用户回答数与文章数之间的关系，用于观察问答贡献和文章创作之间的分布特征。
7. 中文姓氏词云
   对用户昵称进行姓氏提取，支持复姓识别，并过滤非姓氏字符，使词云统计结果更加准确。

## 八、项目运行方式

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库连接

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=zhihu_bigdata
DB_USER=pdi_user
DB_PASSWORD=你的数据库密码
```

### 3. 创建数据库表

```bash
mysql -u pdi_user -p < sql/01_create_tables.sql
```

### 4. 使用 Kettle/PDI 导入数据

使用 PDI 转换文件完成以下步骤：

```text
读取 JSON 数据
字段清洗
字段选择
写入云端 MySQL
```

导入完成后可检查数据条数：

```bash
mysql -u pdi_user -p -e "USE zhihu_bigdata; SELECT COUNT(*) FROM zhihu_user;"
```

### 5. 运行 PySpark 统计程序

```bash
./run_all_spark_jobs.sh
```

### 6. 启动 Flask 服务

```bash
python webapp/app.py
```

浏览器访问：

```text
http://服务器公网IP:5000/
```

如果已经使用 Nginx + Gunicorn 部署，则访问：

```text
http://服务器公网IP/
```

## 九、部署方式

项目可使用 Gunicorn + Nginx 部署。
Gunicorn 负责运行 Flask 应用：

```bash
gunicorn -w 2 -b 127.0.0.1:5000 webapp.app:app
```

Nginx 负责反向代理到本地 5000 端口。
部署完成后，可通过以下命令检查服务状态：

```bash
systemctl status zhihu-dashboard --no-pager
systemctl status nginx --no-pager
```

## 十、项目特色

本项目不仅完成了基础的数据导入与统计展示，还在以下方面进行了增强：
1. 完整的数据处理链路
   从 JSON 数据清洗、MySQL 入库、PySpark 统计到 Web 可视化展示，形成完整的大数据处理流程。
2. 基于 PySpark 的统计分析
   所有核心统计结果均通过 PySpark 从云端 MySQL 中读取并计算生成，体现分布式计算框架的使用。
3. 姓氏词云清洗优化
   不是简单截取昵称第一个字，而是加入常见姓氏白名单和复姓识别逻辑，过滤昵称中的无意义字符，提高统计结果可信度。
4. 用户活跃度分析
   通过回答数分布、文章数分布和 Top10 高回答用户排行，分析用户内容贡献情况。
5. 多维可视化展示
   使用 ECharts 展示柱状图、环形图、横向排行图、散点图和词云图，使分析结果更加直观。
6. 云端部署
   项目部署在云服务器上，通过 Nginx 和 Gunicorn 提供公网访问能力。

## 十一、运行结果

系统页面展示内容包括：

```text
用户总数 KPI
平均回答数 KPI
平均文章数 KPI
最高回答数 KPI
最高文章数 KPI
回答数分布直方图
文章数分布直方图
性别比例环形图
Top10 高回答用户排行
回答数-文章数关系散点图
中文姓氏词云
```

## 十二、总结

本项目完成了一个较完整的知乎用户大数据分析平台。通过 Kettle/PDI 实现数据清洗与入库，通过 PySpark 完成统计分析，通过 Flask 和 ECharts 实现可视化展示，并最终部署到云服务器。项目覆盖了数据采集结果处理、数据库管理、分布式计算、Web 开发和云端部署等多个环节，能够较好体现大数据与云计算课程设计的综合实践能力。
