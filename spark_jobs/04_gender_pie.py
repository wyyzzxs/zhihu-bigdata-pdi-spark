from pyspark.sql import functions as F
from common import get_spark, read_users, save_json

spark = get_spark("04_gender_pie")
df = read_users(spark)

gender_label = (
    F.when(F.col("gender").cast("int") == 1, "男")
    .when(F.col("gender").cast("int") == 0, "女")
    .otherwise("未知")
)

rows = (
    df.withColumn("gender_name", gender_label)
    .groupBy("gender_name")
    .count()
    .orderBy(F.desc("count"))
    .collect()
)

data = [{"name": r["gender_name"], "value": int(r["count"])} for r in rows]

save_json("gender_pie.json", data)
spark.stop()
