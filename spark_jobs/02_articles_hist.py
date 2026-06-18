from common import get_spark, read_users, save_json, histogram

spark = get_spark("02_articles_hist")
df = read_users(spark)

data = histogram(df, "articles_count")
save_json("articles_hist.json", data)

spark.stop()
