### FILE: lt_fishing/auto_fishing.py
import cv2
import numpy as np
import pyautogui
import time
from mss import mss
from PIL import Image

class AutoFishing:
    def __init__(self, template_path, threshold=0.8):
        self.template = cv2.imread(template_path, 0)
        self.tw, self.th = self.template.shape[::-1]
        self.threshold = threshold
        self.running = False
        self.success_count = 0
        self.fail_count = 0
        self.window_title = None

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running

    def set_target_window(self, title):
        self.window_title = title

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
        screen = self.capture_fullscreen()
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

### FILE: lt_fishing/main.py
import tkinter as tk
from tkinter import ttk
import threading
import time
from auto_fishing import AutoFishing
import win32gui
import win32process
import psutil

class LTFishingGUI:
    def set_styles(self):
        style = ttk.Style()
        style.configure("Bold.TButton", font=("Arial", 10, "bold"))
    def __init__(self, root):
        self.root = root
        self.root.title("LT Fishing Python")
        self.root.geometry("320x347")
        self.root.configure(bg='#f4a7b9')
        self.root.iconbitmap("logo.ico")

        self.bot = AutoFishing("template.png")
        self.thread = None

        self.build_ui()
        self.set_styles()
        self.update_stats()
        self.refresh()

    def build_ui(self):
        container = tk.Frame(self.root, bg='#f4a7b9')
        container.pack(pady=10)

        def grid_button(row, col, text, cmd=None, colspan=1):
            btn = ttk.Button(container, text=text, command=cmd or (lambda: print(text, style="Bold.TButton")))
            btn.grid(row=row, column=col, columnspan=colspan, padx=5, pady=5, sticky="ew")
            return btn

        grid_button(0, 0, "Làm mới", self.refresh)
        self.ld_entry = ttk.Combobox(container, state="readonly")
        self.ld_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        grid_button(0, 2, "Kết nối", self.connect_ld)

        grid_button(1, 0, "Bắt đầu", self.start_bot)
        grid_button(1, 1, "Bán cá", self.sell_fish)
        grid_button(1, 2, "Tạm dừng", self.stop_bot)

        ttk.Label(container, text="Vị trí cần", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=1)
        self.slot = ttk.Combobox(container, values=["1", "2", "3", "4", "5"], state="readonly")
        self.slot.set("1")
        self.slot.grid(row=2, column=1, sticky="ew")
        grid_button(2, 2, "Lọc bóng", self.filter_shadow)

        grid_button(3, 0, "Đặt lại", self.reset_stats)
        grid_button(3, 1, "Khóa máy", self.lock_pc)
        grid_button(3, 2, "Tắt máy", self.shutdown)

        stats_frame = tk.Frame(self.root, bg='#f4a7b9')
        stats_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.stats_label = tk.Label(stats_frame, text="", bg='#f4a7b9', font=("Arial", 10), anchor="w")
        self.stats_label.pack(anchor="w")

        self.stats_label2 = tk.Label(stats_frame, text="", bg='#f4a7b9', font=("Arial", 10), anchor="w")
        self.stats_label2.pack(anchor="w", pady=(5, 0))

    def refresh(self):
        self.ld_entry.set("")
        self.stats_label.config(text="Đang chờ...")
        self.stats_label2.config(text="Đang chờ...")
        titles = []

        def enum_handler(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    name = process.name().lower()

                    # Bỏ qua trình quản lý MEmu
                    if name in ["memumanage.exe", "memumanager.exe"]:
                        return

                    # Nhận diện các emulator thật (LDPlayer, MEmu, LdBox...)
                    if any(em in name for em in ["ldplayer", "ldconsole", "ldbox", "memu"]):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            result.append((title, hwnd, pid))

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        win32gui.EnumWindows(enum_handler, titles)
        title_list = [title for title, hwnd, pid in titles]
        self.hwnd_map = {title: hwnd for title, hwnd, pid in titles}
        self.pid_map = {title: pid for title, hwnd, pid in titles}
        self.ld_entry['values'] = [""] + title_list

    def connect_ld(self):
            selected = self.ld_entry.get()
            if selected:
                hwnd = self.hwnd_map.get(selected)
                pid = self.pid_map.get(selected)

                # Gửi cả PID và hwnd vào bot nếu cần
                self.bot.set_target_window(selected)  # có thể mở rộng thêm: hwnd, pid

                print(f"[INFO] Đã chọn cửa sổ: {selected} (PID: {pid})")
                self.stats_label.config(text=f"Đã tìm thấy game tại PID {pid}")
            else:
                print("[WARN] Không có cửa sổ giả lập được chọn")
                self.stats_label.config(text="Không tìm thấy cửa sổ giả lập được chọn")

    def start_bot(self):
        if not self.bot.is_running():
            self.bot.start()
            self.thread = threading.Thread(target=self.run_bot)
            self.thread.daemon = True
            self.thread.start()

    def stop_bot(self):
        self.bot.stop()

    def sell_fish(self):
        print("[INFO] Bán cá tự động chưa được cài")

    def filter_shadow(self):
        print("[INFO] Lọc bóng cá chưa được cài")

    def reset_stats(self):
        self.bot.success_count = 0
        self.bot.fail_count = 0

    def lock_pc(self):
        print("[INFO] Khóa máy chưa được cài")

    def support(self):
        import webbrowser
        webbrowser.open("https://www.buymeacoffee.com")

    def shutdown(self):
        print("[INFO] Tắt máy chưa được cài")

    def run_bot(self):
        while self.bot.is_running():
            self.bot.run_once()

    def update_stats(self):
        # self.stats_label.config(text=f"Thành công: {self.bot.success_count}")
        # self.stats_label2.config(text=f"Thất bại: {self.bot.fail_count}")
        self.root.after(1000, self.update_stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = LTFishingGUI(root)
    root.mainloop()
