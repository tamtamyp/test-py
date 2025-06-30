import cv2
import numpy as np
import pyautogui
import time
import win32gui
from PIL import ImageGrab

class AutoFishing:
    def __init__(self, template_path, threshold=0.8):
        self.template = cv2.imread(template_path, 0)
        self.tw, self.th = self.template.shape[::-1]
        self.threshold = threshold
        self.running = False
        self.success_count = 0
        self.fail_count = 0
        self.hwnd = None  # Dùng để lưu HWND của cửa sổ giả lập

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running

    def set_target_hwnd(self, hwnd):
        self.hwnd = hwnd

    def capture_window(self):
        if not self.hwnd:
            return None
        try:
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            img = ImageGrab.grab(bbox=(left, top, right, bottom))
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"[ERROR] Capture window failed: {e}")
            return None

    def find_target(self, screen):
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= self.threshold:
            return max_loc
        return None

    def run_once(self):
        screen = self.capture_window()
        if screen is None:
            self.fail_count += 1
            time.sleep(0.5)
            return

        pos = self.find_target(screen)
        if pos:
            click_x = pos[0] + self.tw // 2
            click_y = pos[1] + self.th // 2
            pyautogui.click(click_x, click_y)
            self.success_count += 1
            time.sleep(1.2)
        else:
            self.fail_count += 1
        time.sleep(0.5)
