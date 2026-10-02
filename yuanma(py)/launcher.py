import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


class Launcher:
    def __init__(self, root):
        self.root = root
        self.root.title("选择模式")
        self.root.geometry("400x300")

        # 三个 exe 所在目录（跟你这个启动器同目录）
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        ttk.Label(root, text="选择要运行的模式：",
                  font=("Microsoft YaHei", 12)).pack(pady=20)

        for label, exe_name in [
            ("💬 接龙模式",  "chat_relay.exe"),
            ("🗣️ 讨论模式",  "chat_discuss.exe"),
            ("⚔️ 互怼模式",  "chat_battle.exe"),
        ]:
            ttk.Button(root, text=label, width=20,
                       command=lambda e=exe_name: self.run_exe(e)).pack(pady=8)

    def run_exe(self, exe_name):
        path = os.path.join(self.base_dir, exe_name)
        if not os.path.exists(path):
            messagebox.showerror("找不到", f"没有找到：{path}")
            return
        # 不阻塞启动器
        subprocess.Popen([path], cwd=self.base_dir)


if __name__ == "__main__":
    root = tk.Tk()
    Launcher(root)
    root.mainloop()