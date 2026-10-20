"""吸引の効果と必要な電力を見積もる。

1. 吸引力ごとの、グリップで決まる加速度とコーナーの最高速度
2. 吸引する面積と床とのすき間ごとの、負圧とファンの電力
   （すき間から漏れる空気の量 × 負圧 を空気の仕事とする。KOGUMA-Mk4 の docs/spec.md と同じ考え方）

    python3 tools/suction_estimate.py
    python3 tools/suction_estimate.py --mass 140 --mu 1.0
"""
import argparse
import math

G = 9.81
RHO = 1.2           # 空気の密度 [kg/m³]
CD = 0.6            # すき間の流量係数
FAN_EFF = 0.3       # ファン全体の効率（電気 → 空気）
SUCTIONS = (0, 100, 200, 300, 400)          # 吸引力 [gf]
RADII = (0.1, 0.2, 0.5)                     # コーナー半径 [m]
AREAS = ((40, 50), (60, 80))                # 吸引する範囲 [mm × mm]
GAPS = (0.2, 0.5, 1.0)                      # スカートと床のすき間 [mm]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mass', type=float, default=140.0, help='機体質量 [g]')
    ap.add_argument('--mu', type=float, default=1.0, help='タイヤと床の摩擦係数')
    ap.add_argument('--suction', type=float, default=300.0, help='電力の計算に使う吸引力 [gf]')
    a = ap.parse_args()
    m = a.mass / 1000

    print(f"機体 {a.mass:.0f}g, μ = {a.mu}")
    print("吸引力   グリップの上限   コーナーの最高速度 " + " ".join(f"R{r * 1000:.0f}" for r in RADII))
    for s in SUCTIONS:
        a_max = a.mu * (m * G + s / 1000 * G) / m
        vs = " ".join(f"{math.sqrt(a_max * r):4.2f}" for r in RADII)
        print(f"{s:4d}gf   {a_max:5.1f} m/s²       {vs}  [m/s]")

    f = a.suction / 1000 * G
    print(f"\n吸引力 {a.suction:.0f}gf に必要な負圧と電力（効率 {FAN_EFF}）")
    for w, h in AREAS:
        area = w * h * 1e-6
        perim = 2 * (w + h) * 1e-3
        dp = f / area
        vel = math.sqrt(2 * dp / RHO)
        cols = []
        for gap in GAPS:
            q = CD * perim * gap * 1e-3 * vel
            cols.append(f"すき間{gap}mm: {q * dp / FAN_EFF:5.1f}W")
        print(f"  {w}×{h}mm  負圧 {dp / 1000:.2f}kPa  " + "  ".join(cols))


if __name__ == '__main__':
    main()
