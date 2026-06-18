# 10W+知乎用户数据分析系统

## 1. 项目简介

本项目是《大数据与云计算》综合设计作业，使用 PDI/Kettle 社区版完成数据清洗与云端 MySQL 入库，使用 PySpark 完成统计计算，使用 Flask + ECharts 部署网页展示统计结果。

## 2. 技术路线

数据集 items.json  
→ PDI-CE/Kettle 清洗字段、处理空值、类型转换  
→ 导入阿里云 Ubuntu 服务器 MySQL  
→ PySpark 从 MySQL 读取数据并计算统计结果  
→ Flask Web 服务展示图表  
→ Nginx 对外提供浏览器访问

## 3. 统计内容

- 发文数量分布直方图
- 回答问题数量分布直方图
- 性别比例饼图
- 姓名中姓的词云图
- 数据总览统计

## 4. 目录说明

- sql：数据库建表脚本
- pdi：PDI/Kettle 转换文件
- spark_jobs：PySpark 统计程序
- webapp：Flask 网页展示程序
- docs/screenshots：运行截图

## 5. 运行方式

### 5.1 创建数据库表

```bash
mysql -u pdi_user -p zhihu_bigdata < sql/01_create_tables.sql
```

5.2 运行 PySpark 统计程序

```bash
./run_all_spark_jobs.sh
```

5.3 启动网页

```bash
source .venv/bin/activate
python webapp/app.py
```

正式部署使用 systemd + Nginx。

6. 说明

原始数据文件 items.json 较大，不上传到代码仓库。数据库密码写入 .env，本仓库只保留 .env.example。
