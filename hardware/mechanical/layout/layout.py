"""機体の配置の案を、部品の箱（直方体）で置いて確かめる。

- 重さの合計、重心、ヨー（旋回）の慣性モーメント
- 床への投影が収まる最小の円の直径（規定は直径 25cm 以内）
- ショートカットできる幅（機体の投影がラインから完全に離れない範囲）
- 上から見た図と横から見た図（SVG）

座標は車軸の中心の真下を原点にする。+x が前、+y が左、z が上（床が 0）。単位は mm と g。

    python3 hardware/mechanical/layout/layout.py docs/img/layout_v0.svg
"""
import math
import sys

TIRE_D = 24.0
WHEEL_Y = 45.0          # 車輪の中心の y（トレッド 90mm）
WHEEL_W = 10.0
GEAR_CENTER = 12.6      # 車軸からモータ中心まで（13T:71T、m0.3）
MOTOR_D, MOTOR_L = 8.6, 20.0
MOTOR_FACE_Y = 37.0     # モータの前の面（軸の側）の |y|
AXLE_Z = TIRE_D / 2
LINE_HALF = 9.5         # ライン幅 19mm の半分

# 名前、色、(x 最小, x 最大), (y 最小, y 最大), (z 最小, z 最大), 質量
PARTS = []


def box(name, color, x, y, z, mass):
    PARTS.append(dict(name=name, color=color, x=x, y=y, z=z, mass=mass))


def both_sides(name, color, x, y, z, mass):
    box(name + '（左）', color, x, y, z, mass)
    box(name + '（右）', color, x, (-y[1], -y[0]), z, mass)


# 車輪（タイヤ・ホイール・71T・車軸・軸受）
both_sides('車輪', '#333333', (-TIRE_D / 2, TIRE_D / 2), (WHEEL_Y - WHEEL_W / 2, WHEEL_Y + WHEEL_W / 2),
           (0, TIRE_D), 2.5)
# 走行用モータ 1 輪 3 個（前・上・後ろ）
for label, ang in (('前', 0), ('上', 90), ('後ろ', 180)):
    cx = GEAR_CENTER * math.cos(math.radians(ang))
    cz = AXLE_Z + GEAR_CENTER * math.sin(math.radians(ang))
    both_sides('モータ' + label, '#9e9e9e', (cx - MOTOR_D / 2, cx + MOTOR_D / 2),
               (MOTOR_FACE_Y - MOTOR_L, MOTOR_FACE_Y), (cz - MOTOR_D / 2, cz + MOTOR_D / 2), 5.3)
# エンコーダ MES-6（車軸と同じ軸、モータに囲まれた内側）
both_sides('エンコーダ', '#e15759', (-3.75, 3.75), (22.0, 36.0), (AXLE_Z - 3.75, AXLE_Z + 3.75), 5.0)
# モータマウント
both_sides('マウント', '#f28e2b', (-20, 20), (16, 38), (3, 30), 2.0)
# 吸引ファン（羽根 φ32、囲い φ33 → 箱で近似）
box('吸引ファン', '#59a14f', (-53, -19), (-17, 17), (4, 24), 7.5)
# 電池（2S 300mAh、仮に 52 × 30 × 12mm）。車軸の前、フレームの上
box('電池', '#4e79a7', (19, 49), (-26, 26), (4, 16), 20.0)
# メイン基板＋部品（MCU、ドライバ、IMU × 2 など）
box('メイン基板', '#76b7b2', (-55, 50), (-36, 36), (31, 33), 9.0)
# センサ基板（ラインセンサ 14 ＋ マーカー 2、AD7490）
box('センサ基板', '#edc948', (55, 65), (-75, 75), (3, 5), 3.0)
# フレーム・スカート・滑り板
box('フレーム', '#bab0ac', (-55, 55), (-36, 36), (2, 3.5), 8.0)
# ねじ・配線
box('ねじ・配線', '#bab0ac', (-30, 30), (-30, 30), (3, 30), 3.0)

SUCTION = ((-45, 40), (-30, 30))   # 吸引する範囲（フレームの下）


def footprint_points():
    pts = []
    for p in PARTS:
        for x in p['x']:
            for y in p['y']:
                pts.append((x, y))
    return pts


def min_circle(pts):
    """外側の点を全部含む最小の円（粗い格子探索 → 細かく）。"""
    best = (0.0, 0.0, 1e9)
    cx, cy, step = 0.0, 0.0, 20.0
    for _ in range(6):
        for i in range(-10, 11):
            for j in range(-10, 11):
                x, y = cx + i * step, cy + j * step
                r = max(math.hypot(px - x, py - y) for px, py in pts)
                if r < best[2]:
                    best = (x, y, r)
        cx, cy, step = best[0], best[1], step / 5
    return best


def summary():
    m = sum(p['mass'] for p in PARTS)
    cg = [sum(p['mass'] * (p[k][0] + p[k][1]) / 2 for p in PARTS) / m for k in ('x', 'y', 'z')]
    izz = 0.0
    for p in PARTS:
        dx, dy = p['x'][1] - p['x'][0], p['y'][1] - p['y'][0]
        px, py = (p['x'][0] + p['x'][1]) / 2, (p['y'][0] + p['y'][1]) / 2
        izz += p['mass'] * ((dx ** 2 + dy ** 2) / 12 + px ** 2 + py ** 2)
    cx, cy, r = min_circle(footprint_points())
    print(f"合計 {m:.1f} g")
    print(f"重心 x={cg[0]:.1f} y={cg[1]:.1f} z={cg[2]:.1f} mm（車軸の真下が原点）")
    print(f"ヨーの慣性モーメント（車軸の中心まわり） {izz / 100:.0f} g·cm²")
    print(f"床への投影が収まる最小の円 直径 {2 * r:.0f} mm（中心 x={cx:.0f}, y={cy:.0f}）。規定は 250mm 以内")
    half = max(abs(y) for p in PARTS for y in p['y'])
    print(f"機体の最大の横幅 {2 * half:.0f} mm → 機体の中心をラインから最大 ±{half + LINE_HALF:.0f} mm 離せる")
    (x0, x1), (y0, y1) = SUCTION
    print(f"吸引する範囲 {x1 - x0:.0f} × {y1 - y0:.0f} mm = {(x1 - x0) * (y1 - y0) / 100:.0f} cm²")
    return (cx, cy, r), cg


def svg(path, circle, cg):
    s = 2.0  # 1mm = 2px
    w, h = 640, 860
    ox, oy = 320, 330      # 上から見た図の原点（x が上向き）
    sx, sz = 320, 830      # 横から見た図の原点
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="IPAGothic, sans-serif" font-size="12">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<text x="10" y="20" font-size="15">上から見た図（前が上）</text>']
    cx, cy, r = circle
    out.append(f'<circle cx="{ox - cy * s}" cy="{oy - cx * s}" r="{r * s}" fill="none" stroke="#aaa" stroke-dasharray="4 4"/>')
    out.append(f'<circle cx="{ox - cy * s}" cy="{oy - cx * s}" r="{125 * s}" fill="none" stroke="#e15759" stroke-dasharray="2 6"/>')
    (x0, x1), (y0, y1) = SUCTION
    out.append(f'<rect x="{ox - y1 * s}" y="{oy - x1 * s}" width="{(y1 - y0) * s}" height="{(x1 - x0) * s}" '
               'fill="#59a14f" fill-opacity="0.08" stroke="#59a14f" stroke-dasharray="3 3"/>')
    order = sorted(PARTS, key=lambda p: p['z'][1])
    for p in order:
        out.append(f'<rect x="{ox - p["y"][1] * s}" y="{oy - p["x"][1] * s}" width="{(p["y"][1] - p["y"][0]) * s}" '
                   f'height="{(p["x"][1] - p["x"][0]) * s}" fill="{p["color"]}" fill-opacity="0.45" stroke="{p["color"]}"/>')
    out.append(f'<line x1="{ox - 130 * s}" y1="{oy}" x2="{ox + 130 * s}" y2="{oy}" stroke="#000" stroke-width="0.5"/>')
    out.append(f'<circle cx="{ox - cg[1] * s}" cy="{oy - cg[0] * s}" r="4" fill="#000"/>')
    labels = [('センサ基板', 60, 0), ('電池', 34, 0), ('吸引ファン', -36, 0), ('モータ ×3', 0, 27), ('モータ ×3', 0, -27),
              ('車輪', 18, 45), ('車輪', 18, -45)]
    for t, x, y in labels:
        out.append(f'<text x="{ox - y * s}" y="{oy - x * s + 4}" text-anchor="middle">{t}</text>')
    out.append(f'<text x="{ox + 8}" y="{oy - cg[0] * s - 6}">重心</text>')
    out.append(f'<text x="10" y="{oy + 230}" fill="#e15759">赤の点線: 直径 250mm の円（規定）　灰の点線: 実際に収まる最小の円　緑: 吸引する範囲</text>')
    t = 3.0  # 横から見た図は 1mm = 3px
    out.append(f'<text x="10" y="{sz - 130}" font-size="15">横から見た図（前が右、左側の部品、拡大）</text>')
    out.append(f'<line x1="20" y1="{sz}" x2="{w - 20}" y2="{sz}" stroke="#000"/>')
    out.append(f'<text x="24" y="{sz + 16}">床</text>')
    for p in sorted(PARTS, key=lambda p: -p['y'][1]):
        if p['y'][1] < 0:
            continue
        out.append(f'<rect x="{sx + p["x"][0] * t}" y="{sz - p["z"][1] * t}" width="{(p["x"][1] - p["x"][0]) * t}" '
                   f'height="{(p["z"][1] - p["z"][0]) * t}" fill="{p["color"]}" fill-opacity="0.45" stroke="{p["color"]}"/>')
    out.append(f'<circle cx="{sx}" cy="{sz - AXLE_Z * t}" r="{TIRE_D / 2 * t}" fill="none" stroke="#333"/>')
    for txt, x, z in (('メイン基板', 0, 35), ('センサ', 60, 8), ('電池', 34, 10), ('ファン', -36, 14), ('モータ', 0, 28)):
        out.append(f'<text x="{sx + x * t}" y="{sz - z * t}" text-anchor="middle">{txt}</text>')
    out.append('</svg>')
    with open(path, 'w') as f:
        f.write('\n'.join(out))


if __name__ == '__main__':
    circle, cg = summary()
    if len(sys.argv) > 1:
        svg(sys.argv[1], circle, cg)
        print('図:', sys.argv[1])
