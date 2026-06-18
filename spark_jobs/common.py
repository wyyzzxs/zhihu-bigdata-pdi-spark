import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "webapp" / "static" / "data"
IMG_DIR = ROOT_DIR / "webapp" / "static" / "img"

DATA_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)


def get_spark(app_name: str) -> SparkSession:
    jdbc_jar = os.getenv("JDBC_JAR")
    if not jdbc_jar or not Path(jdbc_jar).exists():
        raise FileNotFoundError(f"JDBC_JAR 不存在，请检查 .env：{jdbc_jar}")

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.jars", jdbc_jar)
        .config("spark.driver.extraClassPath", jdbc_jar)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_users(spark: SparkSession):
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    db = os.getenv("DB_NAME", "zhihu_bigdata")
    user = os.getenv("DB_USER", "app_user")
    password = os.getenv("DB_PASSWORD")
    table = os.getenv("DB_TABLE", "zhihu_user")

    if not password:
        raise ValueError("请在 .env 中配置 DB_PASSWORD")

    url = (
        f"jdbc:mysql://{host}:{port}/{db}"
        "?useSSL=false"
        "&serverTimezone=Asia/Shanghai"
        "&characterEncoding=utf8"
        "&allowPublicKeyRetrieval=true"
    )

    return (
        spark.read.format("jdbc")
        .option("url", url)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("dbtable", table)
        .option("user", user)
        .option("password", password)
        .load()
    )


def save_json(filename: str, data):
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 写入 {path}")


def histogram(df, column_name: str):
    v = F.coalesce(F.col(column_name).cast("long"), F.lit(0))

    bucket = (
        F.when(v == 0, "0")
        .when(v == 1, "1")
        .when((v >= 2) & (v <= 5), "2-5")
        .when((v >= 6) & (v <= 10), "6-10")
        .when((v >= 11) & (v <= 20), "11-20")
        .when((v >= 21) & (v <= 50), "21-50")
        .when((v >= 51) & (v <= 100), "51-100")
        .when((v >= 101) & (v <= 200), "101-200")
        .when((v >= 201) & (v <= 500), "201-500")
        .when((v >= 501) & (v <= 1000), "501-1000")
        .otherwise("1000+")
    )

    labels = [
        "0", "1", "2-5", "6-10", "11-20", "21-50",
        "51-100", "101-200", "201-500", "501-1000", "1000+"
    ]

    rows = (
        df.withColumn("bucket", bucket)
        .groupBy("bucket")
        .count()
        .collect()
    )

    count_map = {r["bucket"]: int(r["count"]) for r in rows}
    return [{"name": label, "value": count_map.get(label, 0)} for label in labels]
