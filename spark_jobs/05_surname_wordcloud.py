import json
import os
from pathlib import Path

from pyspark.sql import functions as F
from wordcloud import WordCloud

from common import get_spark, read_users, save_json, DATA_DIR, IMG_DIR

spark = get_spark("05_surname_wordcloud")
df = read_users(spark)

name_col = F.trim(F.coalesce(F.col("name"), F.lit("")))

surname_col = F.regexp_extract(name_col, r"^([\u4e00-\u9fff])", 1)

rows = (
    df.withColumn("surname", surname_col)
    .filter(F.col("surname") != "")
    .groupBy("surname")
    .count()
    .orderBy(F.desc("count"))
    .limit(200)
    .collect()
)

data = [{"name": r["surname"], "value": int(r["count"])} for r in rows]
save_json("surname_wordcloud.json", data)

font_path = os.getenv(
    "WORDCLOUD_FONT",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
)

freq = {item["name"]: item["value"] for item in data}

if freq:
    wc = WordCloud(
        font_path=font_path,
        width=1200,
        height=700,
        background_color="white",
        max_words=120,
        collocations=False
    )
    wc.generate_from_frequencies(freq)
    out = IMG_DIR / "surname_wordcloud.png"
    wc.to_file(str(out))
    print(f"[OK] 写入 {out}")
else:
    print("[WARN] 没有生成词云：没有有效中文姓名")

spark.stop()
