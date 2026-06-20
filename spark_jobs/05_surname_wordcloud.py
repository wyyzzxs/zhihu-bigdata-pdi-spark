import json
import os
import re
from collections import Counter

from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from wordcloud import WordCloud

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "webapp", "static", "data")
IMG_DIR = os.path.join(BASE_DIR, "webapp", "static", "img")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "zhihu_bigdata")
DB_USER = os.getenv("DB_USER", "pdi_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

JAR_PATH = os.path.join(BASE_DIR, "drivers", "mysql-connector-j-8.0.33.jar")

COMPOUND_SURNAMES = [
    "欧阳", "太史", "端木", "上官", "司马", "东方", "独孤", "南宫", "万俟", "闻人",
    "夏侯", "诸葛", "尉迟", "公羊", "赫连", "澹台", "皇甫", "宗政", "濮阳", "公冶",
    "太叔", "申屠", "公孙", "慕容", "仲孙", "钟离", "长孙", "宇文", "司徒", "鲜于",
    "司空", "闾丘", "子车", "亓官", "司寇", "巫马", "公西", "颛孙", "壤驷", "公良",
    "漆雕", "乐正", "宰父", "谷梁", "拓跋", "夹谷", "轩辕", "令狐", "段干", "百里",
    "呼延", "东郭", "南门", "羊舌", "微生", "公户", "公玉", "公仪", "梁丘", "公仲",
    "公上", "公门", "公山", "公坚", "左丘", "公伯", "西门", "公祖", "第五", "公乘",
    "贯丘", "公皙", "南荣", "东里", "东宫", "仲长", "子书", "子桑", "即墨", "达奚",
    "褚师", "吴铭"
]

SINGLE_SURNAMES = set("""
赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜
戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费
廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和
穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋庞熊纪舒屈项祝董梁杜阮
蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田胡凌霍虞万支
柯昝管卢莫经房裘缪干解应宗丁宣邓郁单杭洪包诸左石崔吉龚程邢滑裴陆
荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯
宓蓬全郗班仰秋仲伊宫宁仇栾暴甘斜厉戎祖武符刘景詹束龙叶幸司韶郜黎
蓟薄印宿白怀蒲台从鄂索咸籍赖卓蔺屠蒙池乔阴胥能苍双闻莘党翟谭贡劳
逄姬申扶堵冉宰郦雍却璩桑桂濮牛寿通边扈燕冀浦尚农温别庄晏柴瞿阎充
慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东
殴殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰
巢关蒯相查后荆红游竺权逯盖益桓公仉督晋楚阎法汝鄢涂钦归海岳帅缑亢
况郈有琴商牟佘佴伯赏墨哈谯笪年爱阳佟言福
""".replace("\n", "").replace(" ", ""))

BAD_PREFIX = set("老小阿大一二三四五六七八九十不无是在人有和的了吃喝看想爱恨很真假")
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]+")


def extract_surname(name):
    if not name:
        return None

    text = "".join(CHINESE_RE.findall(str(name).strip()))
    if not text:
        return None

    for surname in COMPOUND_SURNAMES:
        if text.startswith(surname):
            return surname

    first = text[0]
    if first in SINGLE_SURNAMES and first not in BAD_PREFIX:
        return first

    return None


def find_font():
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic/ukai.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for item in candidates:
        if os.path.exists(item):
            return item
    return None


def main():
    spark = (
        SparkSession.builder
        .appName("ZhihuSurnameWordCloudCleaned")
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
        .select(col("name"))
    )

    names = [row["name"] for row in df.collect()]
    counter = Counter()

    for name in names:
        surname = extract_surname(name)
        if surname:
            counter[surname] += 1

    top_items = counter.most_common(100)

    json_data = [{"name": name, "value": value} for name, value in top_items]
    with open(os.path.join(DATA_DIR, "surname_wordcloud.json"), "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    font_path = find_font()
    wc = WordCloud(
        font_path=font_path,
        width=1200,
        height=650,
        background_color="white",
        max_words=100,
        prefer_horizontal=0.9,
        colormap="viridis",
        margin=4,
        random_state=42,
    )
    wc.generate_from_frequencies(dict(top_items))
    wc.to_file(os.path.join(IMG_DIR, "surname_wordcloud.png"))

    spark.stop()
    print("已生成清洗后的姓氏词云：支持复姓，并过滤非姓氏字符")


if __name__ == "__main__":
    main()
