from common import get_spark, read_users, save_json, histogram

spark = get_spark("03_answers_hist")
df = read_users(spark)

data = histogram(df, "answer_count")
save_json("answers_hist.json", data)

spark.stop()
