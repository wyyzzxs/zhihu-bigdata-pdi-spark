from pyspark.sql import functions as F
from common import get_spark, read_users, save_json

spark = get_spark("01_overview")
df = read_users(spark)

total_users = df.count()

valid_name_users = (
    df.filter(F.col("name").isNotNull() & (F.trim(F.col("name")) != "") & (F.col("name") != "未知"))
    .count()
)

summary = df.select(
    F.avg(F.coalesce(F.col("answer_count").cast("double"), F.lit(0))).alias("avg_answer_count"),
    F.avg(F.coalesce(F.col("articles_count").cast("double"), F.lit(0))).alias("avg_articles_count"),
    F.max(F.coalesce(F.col("answer_count").cast("long"), F.lit(0))).alias("max_answer_count"),
    F.max(F.coalesce(F.col("articles_count").cast("long"), F.lit(0))).alias("max_articles_count"),
).first()

data = {
    "total_users": total_users,
    "valid_name_users": valid_name_users,
    "avg_answer_count": round(float(summary["avg_answer_count"] or 0), 2),
    "avg_articles_count": round(float(summary["avg_articles_count"] or 0), 2),
    "max_answer_count": int(summary["max_answer_count"] or 0),
    "max_articles_count": int(summary["max_articles_count"] or 0),
}

save_json("overview.json", data)
spark.stop()
