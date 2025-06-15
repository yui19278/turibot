import time
import cv2
import numpy as np
import pyautogui
from skimage.metrics import structural_similarity as ssim
from mss import mss

# —— 設定 —— 
MONITOR_INDEX    = 1      
THRESHOLD        = 0.92   # 閾値
CHECK_INTERVAL   = 0.5    # チェック間隔（秒）
# ————————


def get_top_left_quarter(monitor_index: int):
    with mss() as sct:
        mon = sct.monitors[monitor_index]
        x, y = mon["left"], mon["top"]
        w, h = mon["width"], mon["height"]
        return (x, y, w // 2, h // 2)


def capture_gray(region: tuple) -> np.ndarray:
    x, y, w, h = region
    with mss() as sct:
        img = np.array(sct.grab({"left": x, "top": y, "width": w, "height": h}))
    bgr = img[..., :3]  
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)


def main():
    print("待機中...")
    time.sleep(3)

    region   = get_top_left_quarter(MONITOR_INDEX)
    baseline = capture_gray(region)
    print(f"キャプチャを行いました ({baseline.shape[1]}×{baseline.shape[0]})")

    # ループ開始
    while True:

        print("待機中...")
        time.sleep(1)

        cx = region[0] + region[2] // 2
        cy = region[1] + region[3] // 2
        pyautogui.moveTo(cx, cy)
        print("投げ")
        pyautogui.mouseDown()
        time.sleep(0.5)
        pyautogui.mouseUp()

        print("投げ完了")
        time.sleep(2)

        print("釣り中...")
        while True:
            current = capture_gray(region)
            if current.shape != baseline.shape:
                current = cv2.resize(current, (baseline.shape[1], baseline.shape[0]))
            score, _ = ssim(baseline, current, full=True)
            print(f"{score:.3f}", end='\r')

            if score < THRESHOLD:
                print(f"\n {THRESHOLD}! 釣り糸を引き上げます")
                pyautogui.mouseDown()
                time.sleep(20)
                pyautogui.mouseUp()
                break

            time.sleep(CHECK_INTERVAL)

        print("待機中...")
        time.sleep(3)

        print("初めに戻ります")


if __name__ == "__main__":
    main()
