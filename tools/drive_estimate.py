"""駆動系の加速度を見積もる。

DC モータの直線的なトルク-回転数特性を仮定して、車速ごとに出せる最大加速度を計算する。
モータの値は通販の掲載値から推定したもの。実測したら書き換える。

    python3 tools/drive_estimate.py
"""
import math

V = 3.7          # モータ印加電圧 [V]
ETA = 0.8        # ギア効率
R = 0.012        # タイヤ半径 [m]
G = 10           # 減速比
BASE_MASS = 0.140  # 駆動モータを除いた機体質量 [kg]
SPEEDS = (0, 1, 2, 3, 4)  # 評価する車速 [m/s]

# 名前: (無負荷回転数 [rpm], 拘束電流 [A], 質量 [g])
MOTORS = {
    "7x16mm (716)": (47000, 2.0, 3.0),
    "10x20mm (10D)": (39500, 4.9, 5.5),
}


def main():
    for name, (rpm, i_stall, mass_g) in MOTORS.items():
        w0 = rpm * 2 * math.pi / 60
        kt = V / w0
        t_stall = kt * i_stall
        v_max = w0 / G * R
        print(f"\n{name}: Kt={kt * 1e3:.2f} mNm/A, 拘束トルク={t_stall * 1e3:.2f} mNm, "
              f"無負荷最高速={v_max:.1f} m/s")
        for n in (1, 3):
            m = BASE_MASS + 2 * n * mass_g / 1000
            accels = []
            for v in SPEEDS:
                t = t_stall * max(0.0, 1 - v / v_max)
                f = 2 * n * t * G * ETA / R
                accels.append(f / m)
            cols = "  ".join(f"{v}m/s:{a:5.1f}" for v, a in zip(SPEEDS, accels))
            print(f"  {n}個/輪 {m * 1e3:.0f}g  {cols}  [m/s²]  拘束電流合計 {2 * n * i_stall:.0f}A")


if __name__ == "__main__":
    main()
