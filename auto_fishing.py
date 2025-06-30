import cv2
import numpy as np
import pyautogui
import time
from mss import mss
from PIL import Image
import win32gui

class AutoFishing:
    def __init__(self, template_path, threshold=0.8):
        self.template = cv2.imread(template_path, 0)
        self.tw, self.th = self.template.shape[::-1]
        self.threshold = threshold
        self.running = False
        self.success_count = 0
        self.fail_count = 0
        self.window_title = None
        self.window_hwnd = None

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running

    def set_target_window(self, title, hwnd=None):
        print(f"[ERROR] capture_game_window: {hwnd}")
        self.window_title = title
        self.window_hwnd = hwnd

    def capture_game_window(self):
        if not self.window_hwnd:
            return self.capture_fullscreen()

        try:
            rect = win32gui.GetWindowRect(self.window_hwnd)
            x1, y1, x2, y2 = rect
            w, h = x2 - x1, y2 - y1

            with mss() as sct:
                monitor = {"top": y1, "left": x1, "width": w, "height": h}
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"[ERROR] capture_game_window: {e}")
            return self.capture_fullscreen()

    def capture_fullscreen(self):
        with mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def find_target(self, screen):
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= self.threshold:
            return max_loc
        return None

    def run_once(self):
        screen = self.capture_game_window()
        pos = self.find_target(screen)
        if pos:
            click_x = pos[0] + self.tw // 2
            click_y = pos[1] + self.th // 2
            if self.window_hwnd:
                win_x, win_y, _, _ = win32gui.GetWindowRect(self.window_hwnd)
                pyautogui.click(win_x + click_x, win_y + click_y)
            else:
                pyautogui.click(click_x, click_y)
            self.success_count += 1
            time.sleep(1.2)
        else:
            self.fail_count += 1
        time.sleep(0.5)
