#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
source .venv/bin/activate

python spark_jobs/01_overview.py
python spark_jobs/02_articles_hist.py
python spark_jobs/03_answers_hist.py
python spark_jobs/04_gender_pie.py
python spark_jobs/05_surname_wordcloud.py
python spark_jobs/06_top_users.py
python spark_jobs/07_answer_article_scatter.py

echo "全部 PySpark 统计程序运行完成"
