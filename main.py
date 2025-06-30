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
        style.theme_use("clam")  # <<-- Đảm bảo dùng theme hỗ trợ custom font
        style.configure("Bold.TButton", font=("Arial", 10, "bold"))
        style.configure("CustomCombobox.TCombobox", padding=(4, 6, 4, 6), font=("Arial", 10))
    def __init__(self, root):
        self.root = root
        self.root.title("tamtam")
        self.root.geometry("340x347")
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
        self.ld_entry = ttk.Combobox(container, state="readonly", style="CustomCombobox.TCombobox")
        self.ld_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        grid_button(0, 2, "Kết nối", self.connect_ld)

        grid_button(1, 0, "Bắt đầu", self.start_bot)
        grid_button(1, 1, "Bán cá", self.sell_fish)
        grid_button(1, 2, "Tạm dừng", self.stop_bot)

        grid_button(2, 0, "Lọc bóng", self.filter_shadow)

        grid_button(2, 1, "Đặt lại", self.reset_stats)
        grid_button(2, 2, "Khóa máy", self.lock_pc)

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
                    if any(em in name for em in ["ldplayer", "memu"]):
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
