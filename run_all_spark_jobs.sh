#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
source .venv/bin/activate

echo "===== 01 数据总览 ====="
python spark_jobs/01_overview.py

echo "===== 02 发文数量直方图 ====="
python spark_jobs/02_articles_hist.py

echo "===== 03 回答数量直方图 ====="
python spark_jobs/03_answers_hist.py

echo "===== 04 性别饼图 ====="
python spark_jobs/04_gender_pie.py

echo "===== 05 姓名中姓词云 ====="
python spark_jobs/05_surname_wordcloud.py

echo "全部 PySpark 统计程序运行完成"
