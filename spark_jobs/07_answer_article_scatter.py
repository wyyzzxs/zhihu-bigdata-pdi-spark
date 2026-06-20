import json
import os

from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "webapp", "static", "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "zhihu_bigdata")
DB_USER = os.getenv("DB_USER", "pdi_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

JAR_PATH = os.path.join(BASE_DIR, "drivers", "mysql-connector-j-8.0.33.jar")


def main():
    spark = (
        SparkSession.builder
        .appName("ZhihuAnswerArticleScatter")
        .config("spark.jars", JAR_PATH)
        .getOrCreate()
    )

    jdbc_url = (
        f"jdbc:mysql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai"
    )

    df = (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("dbtable", "zhihu_user")
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .load()
    )

    rows = (
        df.select("name", "answer_count", "articles_count", "follower_count")
        .where((col("answer_count") >= 0) & (col("articles_count") >= 0))
        .orderBy(col("follower_count").desc())
        .limit(1200)
        .collect()
    )

    data = [
        {
            "name": row["name"] or "未知用户",
            "answer_count": int(row["answer_count"] or 0),
            "articles_count": int(row["articles_count"] or 0),
            "follower_count": int(row["follower_count"] or 0),
        }
        for row in rows
    ]

    with open(os.path.join(DATA_DIR, "answer_article_scatter.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    spark.stop()
    print("已生成回答数-文章数散点图数据")


if __name__ == "__main__":
    main()
