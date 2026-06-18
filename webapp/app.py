import json
from pathlib import Path

from flask import Flask, jsonify, render_template_string

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "static" / "data"

app = Flask(__name__, static_folder="static")


def load_json(filename):
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/api/<filename>")
def api_file(filename):
    data = load_json(filename)
    if data is None:
        return jsonify({"error": f"{filename} not found"}), 404
    return jsonify(data)


@app.route("/")
def index():
    overview = load_json("overview.json") or {}
    return render_template_string("""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>知乎用户数据分析 - 大数据与云计算综合设计</title>
  <script src="/static/js/echarts.min.js"></script>
  <style>
    body {
      margin: 0;
      font-family: Arial, "Microsoft YaHei", sans-serif;
      background: #f5f6fa;
      color: #222;
    }
    header {
      padding: 28px 40px;
      background: #1f2937;
      color: white;
    }
    header h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
    }
    header p {
      margin: 0;
      opacity: .9;
    }
    main {
      padding: 24px 40px 48px 40px;
    }
    .kpis {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }
    .kpi {
      background: white;
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 2px 10px rgba(0,0,0,.06);
    }
    .kpi .label {
      color: #666;
      font-size: 14px;
    }
    .kpi .value {
      margin-top: 8px;
      font-size: 28px;
      font-weight: bold;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    .card {
      background: white;
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 2px 10px rgba(0,0,0,.06);
    }
    .card h2 {
      margin: 0 0 12px 0;
      font-size: 20px;
    }
    .chart {
      width: 100%;
      height: 420px;
    }
    .wide {
      grid-column: 1 / span 2;
    }
    .wordcloud {
      display: block;
      max-width: 100%;
      margin: 0 auto;
      border-radius: 8px;
    }
    footer {
      padding: 20px 40px;
      color: #777;
      text-align: center;
    }
  </style>
</head>
<body>
<header>
  <h1>10W+知乎用户数据分析系统</h1>
  <p>技术路线：PDI/Kettle 清洗导入云端 MySQL → PySpark 统计计算 → Flask + ECharts 网页展示</p>
</header>

<main>
  <section class="kpis">
    <div class="kpi">
      <div class="label">总用户数</div>
      <div class="value">{{ overview.get("total_users", "-") }}</div>
    </div>
    <div class="kpi">
      <div class="label">有效姓名用户数</div>
      <div class="value">{{ overview.get("valid_name_users", "-") }}</div>
    </div>
    <div class="kpi">
      <div class="label">平均回答数</div>
      <div class="value">{{ overview.get("avg_answer_count", "-") }}</div>
    </div>
    <div class="kpi">
      <div class="label">平均发文数</div>
      <div class="value">{{ overview.get("avg_articles_count", "-") }}</div>
    </div>
  </section>

  <section class="grid">
    <div class="card">
      <h2>发文数量分布直方图</h2>
      <div id="articlesChart" class="chart"></div>
    </div>

    <div class="card">
      <h2>回答问题数量分布直方图</h2>
      <div id="answersChart" class="chart"></div>
    </div>

    <div class="card">
      <h2>性别比例饼图</h2>
      <div id="genderChart" class="chart"></div>
    </div>

    <div class="card">
      <h2>最高值概览</h2>
      <div style="font-size:18px; line-height:2;">
        <p>最高回答数：<b>{{ overview.get("max_answer_count", "-") }}</b></p>
        <p>最高发文数：<b>{{ overview.get("max_articles_count", "-") }}</b></p>
        <p>说明：所有统计结果均由 PySpark 从云端 MySQL 读取后计算生成。</p>
      </div>
    </div>

    <div class="card wide">
      <h2>姓名中姓的词云图</h2>
      <img class="wordcloud" src="/static/img/surname_wordcloud.png" alt="姓氏词云图">
    </div>
  </section>
</main>

<footer>
  大数据与云计算综合设计 | PDI-CE + MySQL + PySpark + Flask
</footer>

<script>
async function getJson(name) {
  const res = await fetch("/api/" + name);
  return await res.json();
}

function renderBar(domId, title, data) {
  const chart = echarts.init(document.getElementById(domId));
  chart.setOption({
    tooltip: { trigger: "axis" },
    grid: { left: 50, right: 20, top: 40, bottom: 60 },
    xAxis: {
      type: "category",
      data: data.map(x => x.name),
      axisLabel: { rotate: 35 }
    },
    yAxis: { type: "value" },
    series: [{
      name: title,
      type: "bar",
      data: data.map(x => x.value)
    }]
  });
}

function renderPie(domId, data) {
  const chart = echarts.init(document.getElementById(domId));
  chart.setOption({
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [{
      name: "性别",
      type: "pie",
      radius: "65%",
      data: data
    }]
  });
}

async function main() {
  const articles = await getJson("articles_hist.json");
  const answers = await getJson("answers_hist.json");
  const gender = await getJson("gender_pie.json");

  renderBar("articlesChart", "发文数量", articles);
  renderBar("answersChart", "回答问题数量", answers);
  renderPie("genderChart", gender);
}

main();
</script>
</body>
</html>
""",overview=overview)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
