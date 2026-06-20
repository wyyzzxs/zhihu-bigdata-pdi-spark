import json
import os

from flask import Flask, jsonify, render_template_string, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "webapp", "static", "data")
IMG_DIR = os.path.join(BASE_DIR, "webapp", "static", "img")

app = Flask(__name__)


def load_json(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    overview = load_json("overview.json", {})
    return render_template_string("""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>知乎用户大数据分析平台</title>
  <script src="/static/js/echarts.min.js"></script>
  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      background: #f4f7fb;
      color: #172033;
    }

    .page {
      width: min(1480px, calc(100% - 48px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }

    .hero {
      border-radius: 18px;
      padding: 30px 34px;
      background:
        radial-gradient(circle at 90% 12%, rgba(45, 212, 191, 0.22), transparent 32%),
        linear-gradient(135deg, #102a56, #176b87 52%, #22a699);
      color: white;
      box-shadow: 0 18px 40px rgba(16, 42, 86, 0.22);
      margin-bottom: 22px;
    }

    .hero h1 {
      margin: 0 0 10px;
      font-size: 32px;
      letter-spacing: 0;
    }

    .hero p {
      margin: 0;
      opacity: 0.88;
      font-size: 15px;
      line-height: 1.7;
    }

    .tech {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
    }

    .tag {
      padding: 6px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.16);
      border: 1px solid rgba(255, 255, 255, 0.22);
      font-size: 13px;
    }

    .kpis {
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }

    .kpi {
      min-height: 112px;
      border-radius: 14px;
      background: white;
      padding: 18px;
      box-shadow: 0 8px 24px rgba(18, 38, 63, 0.08);
      border: 1px solid #e7edf5;
    }

    .kpi .label {
      font-size: 13px;
      color: #667085;
      margin-bottom: 10px;
    }

    .kpi .value {
      font-size: 25px;
      font-weight: 800;
      color: #102a56;
      word-break: break-all;
    }

    .kpi .hint {
      margin-top: 8px;
      font-size: 12px;
      color: #8a94a6;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }

    .card {
      background: white;
      border-radius: 14px;
      padding: 20px;
      box-shadow: 0 8px 24px rgba(18, 38, 63, 0.08);
      border: 1px solid #e7edf5;
      min-height: 420px;
    }

    .card.wide {
      grid-column: span 2;
    }

    .card-title {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .card-title h2 {
      margin: 0;
      font-size: 18px;
      color: #111827;
    }

    .card-title span {
      font-size: 12px;
      color: #8a94a6;
    }

    .chart {
      width: 100%;
      height: 340px;
    }

    .chart.large {
      height: 430px;
    }

    .wordcloud-img {
      width: 100%;
      height: 430px;
      object-fit: contain;
      display: block;
      border-radius: 10px;
      background: #fbfcff;
    }

    .note {
      margin-top: 18px;
      padding: 16px 18px;
      border-radius: 14px;
      background: #edf8ff;
      color: #33516b;
      font-size: 14px;
      line-height: 1.8;
      border: 1px solid #d5edf8;
    }

    @media (max-width: 1100px) {
      .kpis {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
      .grid {
        grid-template-columns: 1fr;
      }
      .card.wide {
        grid-column: span 1;
      }
    }

    @media (max-width: 720px) {
      .page {
        width: min(100% - 24px, 1480px);
      }
      .kpis {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      .hero h1 {
        font-size: 24px;
      }
    }
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>知乎用户大数据分析平台</h1>
      <p>基于 Kettle/PDI 完成 JSON 数据清洗与云端 MySQL 入库，使用 PySpark 对用户内容贡献、性别结构、姓氏分布和高活跃用户进行统计分析，并通过 Flask + ECharts 进行可视化展示。</p>
      <div class="tech">
        <div class="tag">Kettle / PDI</div>
        <div class="tag">Aliyun MySQL</div>
        <div class="tag">PySpark</div>
        <div class="tag">Flask</div>
        <div class="tag">ECharts</div>
        <div class="tag">Nginx + Gunicorn</div>
      </div>
    </section>

    <section class="kpis">
      <div class="kpi">
        <div class="label">用户总数</div>
        <div class="value">{{ "{:,}".format(overview.get("total_users", overview.get("total", 0))|int) }}</div>
        <div class="hint">云端 MySQL 统计样本</div>
      </div>
      <div class="kpi">
        <div class="label">平均回答数</div>
        <div class="value">{{ "%.2f"|format(overview.get("avg_answer_count", overview.get("avg_answers", 0))|float) }}</div>
        <div class="hint">衡量问答活跃度</div>
      </div>
      <div class="kpi">
        <div class="label">平均文章数</div>
        <div class="value">{{ "%.2f"|format(overview.get("avg_articles_count", overview.get("avg_articles", 0))|float) }}</div>
        <div class="hint">衡量创作活跃度</div>
      </div>
      <div class="kpi">
        <div class="label">最高回答数</div>
        <div class="value">{{ "{:,}".format(overview.get("max_answer_count", overview.get("max_answers", 0))|int) }}</div>
        <div class="hint">头部用户贡献明显</div>
      </div>
      <div class="kpi">
        <div class="label">最高文章数</div>
        <div class="value">{{ "{:,}".format(overview.get("max_articles_count", overview.get("max_articles", 0))|int) }}</div>
        <div class="hint">内容生产能力峰值</div>
      </div>
      <div class="kpi">
        <div class="label">数据处理链路</div>
        <div class="value">7 项</div>
        <div class="hint">分布、画像、排行、关系分析</div>
      </div>
    </section>

    <section class="grid">
      <div class="card">
        <div class="card-title">
          <h2>回答数分布直方图</h2>
          <span>用户问答活跃度分层</span>
        </div>
        <div id="answersChart" class="chart"></div>
      </div>

      <div class="card">
        <div class="card-title">
          <h2>文章数分布直方图</h2>
          <span>用户创作活跃度分层</span>
        </div>
        <div id="articlesChart" class="chart"></div>
      </div>

      <div class="card">
        <div class="card-title">
          <h2>性别比例环形图</h2>
          <span>用户画像基础维度</span>
        </div>
        <div id="genderChart" class="chart"></div>
      </div>

      <div class="card">
        <div class="card-title">
          <h2>Top10 高回答用户</h2>
          <span>识别高活跃用户</span>
        </div>
        <div id="topUsersChart" class="chart"></div>
      </div>

      <div class="card wide">
        <div class="card-title">
          <h2>回答数与文章数关系散点图</h2>
          <span>观察问答贡献与文章创作之间的关系</span>
        </div>
        <div id="scatterChart" class="chart large"></div>
      </div>

      <div class="card wide">
        <div class="card-title">
          <h2>中文姓氏词云</h2>
          <span>已支持复姓识别，并过滤非姓氏昵称字符</span>
        </div>
        <img class="wordcloud-img" src="/static/img/surname_wordcloud.png" alt="姓氏词云">
      </div>
    </section>

    <div class="note">
      说明：本系统统计结果由 PySpark 从云端 MySQL 读取并计算生成。姓氏分析阶段加入了常见单姓、复姓白名单，过滤昵称中常见的非姓氏字符，避免“老、是、吃、人”等无意义字符进入词云。
    </div>
  </main>

<script>
const palette = ["#176B87", "#22A699", "#35A7FF", "#F2BE22", "#F29727", "#7C3AED", "#5B8DEF"];
const axisStyle = {
  axisLine: { lineStyle: { color: "#d0d7e2" } },
  axisTick: { show: false },
  axisLabel: { color: "#667085" }
};

async function getJson(url) {
  const res = await fetch(url);
  return await res.json();
}

function renderBar(id, data, color) {
  const chart = echarts.init(document.getElementById(id));
  chart.setOption({
    color: [color],
    tooltip: { trigger: "axis" },
    grid: { left: 54, right: 24, top: 28, bottom: 52 },
    xAxis: {
      type: "category",
      data: data.map(x => x.name || x.range || x.label),
      ...axisStyle,
      axisLabel: { color: "#667085", rotate: 35 }
    },
    yAxis: {
      type: "value",
      ...axisStyle,
      splitLine: { lineStyle: { color: "#edf1f7" } }
    },
    series: [{
      type: "bar",
      data: data.map(x => x.value || x.count || x.cnt),
      barWidth: "52%",
      itemStyle: {
        borderRadius: [7, 7, 0, 0]
      }
    }]
  });
  window.addEventListener("resize", () => chart.resize());
}

async function main() {
  const answers = await getJson("/api/answers_hist");
  const articles = await getJson("/api/articles_hist");
  const gender = await getJson("/api/gender_pie");
  const topUsers = await getJson("/api/top_users");
  const scatter = await getJson("/api/answer_article_scatter");

  renderBar("answersChart", answers, "#176B87");
  renderBar("articlesChart", articles, "#35A7FF");

  const genderChart = echarts.init(document.getElementById("genderChart"));
  genderChart.setOption({
    color: palette,
    tooltip: { trigger: "item" },
    legend: { bottom: 0, textStyle: { color: "#667085" } },
    series: [{
      type: "pie",
      radius: ["46%", "72%"],
      center: ["50%", "46%"],
      avoidLabelOverlap: true,
      label: { formatter: "{b}\\n{d}%" },
      data: gender.map(x => ({
        name: x.name || x.gender_label || x.label,
        value: x.value || x.count || x.cnt
      }))
    }]
  });

  const topChart = echarts.init(document.getElementById("topUsersChart"));
  const topReversed = [...topUsers].reverse();
  topChart.setOption({
    color: ["#22A699"],
    tooltip: {
      trigger: "axis",
      formatter: params => {
        const item = topReversed[params[0].dataIndex];
        return `${item.name}<br>回答数：${item.answer_count}<br>文章数：${item.articles_count}<br>粉丝数：${item.follower_count}`;
      }
    },
    grid: { left: 80, right: 28, top: 20, bottom: 28 },
    xAxis: {
      type: "value",
      ...axisStyle,
      splitLine: { lineStyle: { color: "#edf1f7" } }
    },
    yAxis: {
      type: "category",
      data: topReversed.map(x => x.name),
      ...axisStyle
    },
    series: [{
      type: "bar",
      data: topReversed.map(x => x.answer_count),
      barWidth: 16,
      itemStyle: { borderRadius: [0, 8, 8, 0] }
    }]
  });

  const scatterChart = echarts.init(document.getElementById("scatterChart"));
  scatterChart.setOption({
    color: ["#176B87"],
    tooltip: {
      formatter: p => {
        const item = p.data[3];
        return `${item.name}<br>回答数：${item.answer_count}<br>文章数：${item.articles_count}<br>粉丝数：${item.follower_count}`;
      }
    },
    grid: { left: 66, right: 28, top: 34, bottom: 56 },
    xAxis: {
      name: "回答数",
      type: "value",
      ...axisStyle,
      splitLine: { lineStyle: { color: "#edf1f7" } }
    },
    yAxis: {
      name: "文章数",
      type: "value",
      ...axisStyle,
      splitLine: { lineStyle: { color: "#edf1f7" } }
    },
    dataZoom: [
      { type: "inside" },
      { type: "slider", height: 18, bottom: 18 }
    ],
    series: [{
      type: "scatter",
      symbolSize: val => Math.max(6, Math.min(28, Math.sqrt(val[2] || 1) / 18)),
      data: scatter.map(x => [x.answer_count, x.articles_count, x.follower_count, x]),
      itemStyle: {
        opacity: 0.72
      }
    }]
  });

  window.addEventListener("resize", () => {
    genderChart.resize();
    topChart.resize();
    scatterChart.resize();
  });
}

main();
</script>
</body>
</html>
""", overview=overview)


@app.route("/api/overview")
def api_overview():
    return jsonify(load_json("overview.json", {}))


@app.route("/api/answers_hist")
def api_answers_hist():
    return jsonify(load_json("answers_hist.json", []))


@app.route("/api/articles_hist")
def api_articles_hist():
    return jsonify(load_json("articles_hist.json", []))


@app.route("/api/gender_pie")
def api_gender_pie():
    return jsonify(load_json("gender_pie.json", []))


@app.route("/api/top_users")
def api_top_users():
    return jsonify(load_json("top_users.json", []))


@app.route("/api/answer_article_scatter")
def api_answer_article_scatter():
    return jsonify(load_json("answer_article_scatter.json", []))


@app.route("/static/img/<path:filename>")
def image_file(filename):
    return send_from_directory(IMG_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
