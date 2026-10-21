"""駆動系の加速度を見積もる。

DC モータのモデル I = (V - Ke*ω) / R（Ke = Kt）を使い、電流の上限（ソフトで制限する値）と
電源電圧の両方を考えて、車速ごとに 1 輪あたり n 個のモータで出せる最大加速度を計算する。
タイヤのグリップと転がり抵抗は入れていない。

    python3 tools/drive_estimate.py
    python3 tools/drive_estimate.py --gear 4.38 5.46 --tire 24 --mass 68 --ilim 2.4 --volt 7.4
"""
import argparse

# NFP-D8620-3665-3-7.4（KOGUMA-Mk4 の docs/spec.md のデータシート値）
MOTOR = dict(
    R=1.0,          # 巻線抵抗 [Ω]
    KT=1.47e-3,     # トルク定数 [Nm/A]（逆起電力定数も同じ値とみなす）
    I0=0.14,        # 無負荷電流 [A]
    MASS=5.3e-3,    # 質量 [kg]
)
ETA = 0.8           # ギア効率
SPEEDS = (0, 2, 4, 6)  # 評価する車速 [m/s]


def accel(v, n, gear, tire_d, mass, ilim, volt):
    """車速 v で、1 輪あたり n 個のモータで出せる加速度 [m/s²] と 1 個あたりの電流 [A]。"""
    r = tire_d / 2
    w = v / r * gear                      # モータの角速度 [rad/s]
    i_volt = (volt - MOTOR['KT'] * w) / MOTOR['R']
    i = max(0.0, min(ilim, i_volt))
    torque = MOTOR['KT'] * max(0.0, i - MOTOR['I0'])
    force = 2 * n * torque * gear * ETA / r
    return force / mass, i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gear', type=float, nargs='+', default=[71 / 13], help='減速比')
    ap.add_argument('--tire', type=float, default=24.0, help='タイヤ直径 [mm]')
    ap.add_argument('--mass', type=float, default=68.0, help='駆動モータを除いた機体質量 [g]')
    ap.add_argument('--ilim', type=float, default=2.4, help='モータ 1 個あたりの電流の上限 [A]')
    ap.add_argument('--volt', type=float, default=7.4, help='モータにかけられる電圧 [V]')
    a = ap.parse_args()

    tire_d = a.tire / 1000
    print(f"タイヤ {a.tire:.0f}mm, 電圧 {a.volt}V, 電流上限 {a.ilim}A/個, "
          f"モータ以外 {a.mass:.0f}g, 効率 {ETA}")
    for gear in a.gear:
        v_free = a.volt / MOTOR['KT'] / gear * tire_d / 2
        print(f"\n減速比 {gear:.2f}: 無負荷最高速 約 {v_free:.1f} m/s")
        for n in (1, 2, 3):
            mass = a.mass / 1000 + 2 * n * MOTOR['MASS']
            cols = []
            for v in SPEEDS:
                acc, _ = accel(v, n, gear, tire_d, mass, a.ilim, a.volt)
                cols.append(f"{v}m/s:{acc:5.1f}")
            print(f"  {n}個/輪 {mass * 1e3:4.0f}g  " + "  ".join(cols)
                  + f"  [m/s²]  電流ピーク合計 {2 * n * a.ilim:.0f}A")


if __name__ == '__main__':
    main()
