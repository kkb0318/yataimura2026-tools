# /// script
# requires-python = ">=3.10"
# dependencies = ["weasyprint>=62.0"]
# ///
"""人間ロボットゲーム カード一覧PDF生成ツール

Usage:
    uv run gen_cards.py [output.pdf]
"""

import sys
from pathlib import Path
from weasyprint import HTML

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
@page {
    size: A4;
    margin: 12mm 14mm 10mm 14mm;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Noto Sans CJK JP', 'Noto Sans JP', sans-serif;
    font-size: 8pt;
    color: #212121;
    line-height: 1.3;
}
h1 {
    text-align: center;
    font-size: 15pt;
    font-weight: 700;
    margin-bottom: 6px;
    letter-spacing: 0.05em;
}
hr.top {
    border: none;
    border-top: 0.5px solid #BDBDBD;
    margin-bottom: 8px;
}

/* Section container */
.section {
    border-radius: 5px;
    margin-bottom: 6px;
    overflow: hidden;
}
.section-header {
    padding: 5px 10px;
    color: white;
    font-weight: 700;
    font-size: 9.5pt;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.section-header .count {
    font-weight: 400;
    font-size: 7.5pt;
    opacity: 0.9;
}

/* Blue */
.blue { background: #E8F0FE; }
.blue .section-header { background: #1565C0; }
.blue table tr:nth-child(even) td { background: #D0E4FC; }

/* Yellow */
.yellow { background: #FFF8E1; }
.yellow .section-header { background: #E8A000; }
.yellow table tr:nth-child(even) td { background: #FFECB3; }

/* Red */
.red { background: #FFEBEE; }
.red .section-header { background: #C62828; }
.red table tr:nth-child(even) td { background: #FFCDD2; }

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 7.5pt;
}
thead th {
    text-align: left;
    padding: 3px 6px;
    font-size: 7pt;
    font-weight: 700;
    border-bottom: 1.2px solid rgba(0,0,0,0.2);
}
tbody td {
    padding: 2.5px 6px;
    vertical-align: middle;
}
.col-cat {
    width: 38px;
    font-size: 6.5pt;
    color: #757575;
}
.col-cmd {
    font-weight: 500;
}
.col-num {
    width: 32px;
    text-align: center;
    font-weight: 700;
    font-size: 8pt;
}
.col-use {
    width: 140px;
    font-size: 6.5pt;
    color: #616161;
}

/* Category badges */
.badge {
    display: inline-block;
    padding: 0px 4px;
    border-radius: 3px;
    font-size: 6pt;
    font-weight: 500;
    color: white;
    text-align: center;
    min-width: 28px;
}
.badge-move { background: #43A047; }
.badge-dir { background: #1E88E5; }
.badge-act { background: #8E24AA; }
.badge-loop { background: #F57C00; }
.badge-if { background: #D81B60; }

/* Legend */
.legend {
    background: #F5F5F5;
    border: 0.5px solid #E0E0E0;
    border-radius: 4px;
    padding: 5px 10px;
    margin-top: 4px;
}
.legend-title {
    font-weight: 700;
    font-size: 7.5pt;
    margin-bottom: 3px;
}
.legend-content {
    font-size: 6.8pt;
    color: #616161;
    line-height: 1.5;
}
.legend-badges {
    display: flex;
    gap: 8px;
    margin-bottom: 4px;
    flex-wrap: wrap;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 3px;
}

.footer {
    text-align: center;
    font-size: 5.5pt;
    color: #BDBDBD;
    margin-top: 6px;
}
</style>
</head>
<body>

<h1>人間ロボットゲーム ── カード一覧</h1>
<hr class="top">

<!-- BLUE SECTION -->
<div class="section blue">
  <div class="section-header">
    <span>🔵 青カード（基本）</span>
    <span class="count">合計 14 枚</span>
  </div>
  <table>
    <thead>
      <tr>
        <th class="col-cat">分類</th>
        <th>指令カード</th>
        <th class="col-num">枚数</th>
        <th class="col-use">用途</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="col-cat"><span class="badge badge-move">移動</span></td><td class="col-cmd">1マスすすむ</td><td class="col-num">3</td><td class="col-use">基本移動</td></tr>
      <tr><td class="col-cat"><span class="badge badge-move">移動</span></td><td class="col-cmd">2マスすすむ</td><td class="col-num">2</td><td class="col-use">効率的な移動</td></tr>
      <tr><td class="col-cat"><span class="badge badge-move">移動</span></td><td class="col-cmd">3マスすすむ</td><td class="col-num">1</td><td class="col-use">長距離移動</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">みぎをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">ひだりをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">うしろをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-act">実行</span></td><td class="col-cmd">たからばこ をひらく</td><td class="col-num">2</td><td class="col-use">ゴールアクション</td></tr>
    </tbody>
  </table>
</div>

<!-- YELLOW SECTION -->
<div class="section yellow">
  <div class="section-header">
    <span>🟡 黄カード（中級）</span>
    <span class="count">合計 20 枚</span>
  </div>
  <table>
    <thead>
      <tr>
        <th class="col-cat">分類</th>
        <th>指令カード</th>
        <th class="col-num">枚数</th>
        <th class="col-use">用途</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="col-cat"><span class="badge badge-move">移動</span></td><td class="col-cmd">1マスすすむ</td><td class="col-num">4</td><td class="col-use">基本移動</td></tr>
      <tr><td class="col-cat"><span class="badge badge-move">移動</span></td><td class="col-cmd">2マスすすむ</td><td class="col-num">2</td><td class="col-use">効率的な移動</td></tr>
      <tr><td class="col-cat"><span class="badge badge-move">移動</span></td><td class="col-cmd">3マスすすむ</td><td class="col-num">2</td><td class="col-use">長距離移動</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">みぎをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">ひだりをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">うしろをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-act">実行</span></td><td class="col-cmd">たからばこ をひらく</td><td class="col-num">2</td><td class="col-use">ゴールアクション</td></tr>
      <tr><td class="col-cat"><span class="badge badge-loop">Loop</span></td><td class="col-cmd">[くりかえしおわり]カード までの手順を○回くりかえす</td><td class="col-num">1</td><td class="col-use">ループ開始（○に数字を記入）</td></tr>
      <tr><td class="col-cat"><span class="badge badge-loop">Loop</span></td><td class="col-cmd">くりかえしおわり</td><td class="col-num">1</td><td class="col-use">ループ終了</td></tr>
      <tr><td class="col-cat"><span class="badge badge-act">実行</span></td><td class="col-cmd">[マスのすうじ]のポイントをゲット</td><td class="col-num">2</td><td class="col-use">数字をポイントに加算</td></tr>
    </tbody>
  </table>
</div>

<!-- RED SECTION -->
<div class="section red">
  <div class="section-header">
    <span>🔴 赤カード（上級）</span>
    <span class="count">合計 21 枚</span>
  </div>
  <table>
    <thead>
      <tr>
        <th class="col-cat">分類</th>
        <th>指令カード</th>
        <th class="col-num">枚数</th>
        <th class="col-use">用途</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="col-cat"><span class="badge badge-move">移動</span></td><td class="col-cmd">1マスすすむ</td><td class="col-num">2</td><td class="col-use">基本移動</td></tr>
      <tr><td class="col-cat"><span class="badge badge-move">移動</span></td><td class="col-cmd">2マスすすむ</td><td class="col-num">2</td><td class="col-use">効率的な移動</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">みぎをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">ひだりをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-dir">方向</span></td><td class="col-cmd">うしろをむく</td><td class="col-num">2</td><td class="col-use">方向転換</td></tr>
      <tr><td class="col-cat"><span class="badge badge-act">実行</span></td><td class="col-cmd">たからばこ をひらく</td><td class="col-num">2</td><td class="col-use">ゴールアクション</td></tr>
      <tr><td class="col-cat"><span class="badge badge-act">実行</span></td><td class="col-cmd">[マスのすうじ]のポイントをゲット</td><td class="col-num">2</td><td class="col-use">数字をポイントに加算</td></tr>
      <tr><td class="col-cat"><span class="badge badge-loop">Loop</span></td><td class="col-cmd">[くりかえしおわり1]カード までの手順を○回くりかえす</td><td class="col-num">1</td><td class="col-use">ループ開始（○に数字を記入）</td></tr>
      <tr><td class="col-cat"><span class="badge badge-loop">Loop</span></td><td class="col-cmd">くりかえしおわり1</td><td class="col-num">1</td><td class="col-use">ループ終了（ネスト対応）</td></tr>
      <tr><td class="col-cat"><span class="badge badge-loop">Loop</span></td><td class="col-cmd">[くりかえしおわり2]カード までの手順を○回くりかえす</td><td class="col-num">1</td><td class="col-use">ネストループ開始</td></tr>
      <tr><td class="col-cat"><span class="badge badge-loop">Loop</span></td><td class="col-cmd">くりかえしおわり2</td><td class="col-num">1</td><td class="col-use">ネストループ終了</td></tr>
      <tr><td class="col-cat"><span class="badge badge-if">IF</span></td><td class="col-cmd">もしポイントが6以上なら次のカードを実行する</td><td class="col-num">1</td><td class="col-use">合計値の判定</td></tr>
      <tr><td class="col-cat"><span class="badge badge-if">IF</span></td><td class="col-cmd">もしポイントが6未満なら次のカードを実行する</td><td class="col-num">1</td><td class="col-use">合計値の判定</td></tr>
      <tr><td class="col-cat"><span class="badge badge-if">IF</span></td><td class="col-cmd">もしすうじマスにいるなら次のカードを実行する</td><td class="col-num">1</td><td class="col-use">マス種類の判定</td></tr>
    </tbody>
  </table>
</div>

<!-- Legend -->
<div class="legend">
  <div class="legend-title">凡例・備考</div>
  <div class="legend-content">
    <div class="legend-badges">
      <span class="legend-item"><span class="badge badge-move">移動</span> 前進カード</span>
      <span class="legend-item"><span class="badge badge-dir">方向</span> 方向転換カード</span>
      <span class="legend-item"><span class="badge badge-act">実行</span> アクションカード</span>
      <span class="legend-item"><span class="badge badge-loop">Loop</span> くりかえしカード</span>
      <span class="legend-item"><span class="badge badge-if">IF</span> 条件分岐カード</span>
    </div>
    <div>難易度進行：青（基本操作のみ・14枚）→ 黄（ループ・ポイント追加・20枚）→ 赤（ネストループ・条件分岐・21枚）　─　全3レベル 合計 55枚</div>
  </div>
</div>

<div class="footer">人間ロボットゲーム カード一覧 v2 ─ プログラミング体験ブース教材</div>

</body>
</html>
"""


def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else "card_list.pdf"
    output_path = str(Path(output_path).resolve())
    HTML(string=HTML_TEMPLATE).write_pdf(output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
