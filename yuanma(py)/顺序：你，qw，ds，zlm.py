import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from openai import OpenAI
from api import QWEN_API_KEY, DEEPSEEK_API_KEY, ZHIPU_API_KEY, QWEN_MODEL, DEEPSEEK_MODEL, ZHIPU_MODEL
# ==========================================================


# ==================== 2. System Prompts ====================
SYS_COMMON = """你正在参加一场三人接龙聊天。发言顺序固定：Qwen → DeepSeek → 智谱。
规则：
1. 用户先说话，然后 Qwen 先说，DeepSeek 接着 Qwen 说，智谱最后说。
2. 轮到你时，你会看到：用户刚才说的话 + 前面已经发言的人说过的话。
3. 你不是在孤立地回答用户，你是在“接话”——可以回应前面某人的观点、补充、反驳、或者顺着往下聊。
4. 但不要复述别人说过的内容，也不要总结全场。你只需要说出你自己想说的那一句。
5. 自然口语，150 字以内，不要列清单、不要写代码（除非用户明确要）。
6. 不许客套开场白，上来就说正题。
"""

SYS_QWEN = SYS_COMMON + "\n你的身份：通义千问（Qwen）。你是本轮第一个发言的人。\n风格：温和、有条理、乐于抛出一个可以接下去的点。"
SYS_DS = SYS_COMMON + "\n你的身份：DeepSeek。你是本轮第二个发言的人，前面 Qwen 已经说过。\n风格：犀利、直击本质、可以拆 Qwen 的台，但别为了怼而怼。"
SYS_ZHIPU = SYS_COMMON + "\n你的身份：智谱 GLM。你是本轮最后一个发言的人，前面 Qwen 和 DeepSeek 都说过。\n风格：沉稳、精准、擅长从前面两人忽略的角度切进来收尾。"


class AIChatGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("💬 我 + 三家 AI · 接龙聊天")
        self.root.geometry("1500x820")
        self.root.minsize(1100, 650)

        self.is_running = False
        self.max_history = 20

        # 一份共享的对话历史：所有人（你 + 三家 AI）都在里面，按顺序追加
        self.shared_history = []

        self.qwen_client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.ds_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
        )
        self.zhipu_client = OpenAI(
            api_key=ZHIPU_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4/",
        )

        self._create_widgets()

    # ---------------- UI ----------------
    def _create_widgets(self):
        top = ttk.LabelFrame(self.root, text=" 💬 接龙控制台 ", padding=10)
        top.pack(fill="x", padx=15, pady=10)

        self.btn_clear = ttk.Button(top, text="🗑 清空全部", command=self.clear_all)
        self.btn_clear.pack(side="left", padx=5)

        self.lbl_status = ttk.Label(
            top, text="状态: 就绪，在下方输入你说的话",
            font=("Microsoft YaHei", 9, "italic"),
        )
        self.lbl_status.pack(side="right", padx=15)

        chat_frame = ttk.Frame(self.root)
        chat_frame.pack(fill="both", expand=True, padx=15, pady=5)
        for i in range(3):
            chat_frame.columnconfigure(i, weight=1)
        chat_frame.rowconfigure(0, weight=1)

        qwen_box = ttk.LabelFrame(chat_frame, text=" 🤖 通义千问（第1个说） ", padding=5)
        qwen_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.txt_qwen = tk.Text(qwen_box, wrap="word", font=("Microsoft YaHei", 10))
        self.txt_qwen.pack(fill="both", expand=True)

        ds_box = ttk.LabelFrame(chat_frame, text=" 🐳 DeepSeek（第2个说） ", padding=5)
        ds_box.grid(row=0, column=1, sticky="nsew", padx=5)
        self.txt_ds = tk.Text(ds_box, wrap="word", font=("Microsoft YaHei", 10))
        self.txt_ds.pack(fill="both", expand=True)

        zhipu_box = ttk.LabelFrame(chat_frame, text=" 🧠 智谱 GLM（第3个说） ", padding=5)
        zhipu_box.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self.txt_zhipu = tk.Text(zhipu_box, wrap="word", font=("Microsoft YaHei", 10))
        self.txt_zhipu.pack(fill="both", expand=True)

        bottom = ttk.LabelFrame(self.root, text=" 🎤 你说： ", padding=8)
        bottom.pack(fill="x", padx=15, pady=5)

        self.entry = tk.Text(bottom, height=3, font=("Microsoft YaHei", 10), wrap="word")
        self.entry.pack(side="left", fill="both", expand=True, padx=5)
        self.entry.bind("<Control-Return>", lambda e: (self.send_message(), "break"))

        self.btn_send = ttk.Button(bottom, text="发送\n(Ctrl+Enter)", command=self.send_message)
        self.btn_send.pack(side="left", padx=5, fill="y")

        ttk.Label(
            self.root,
            text="接龙顺序：你 → Qwen → DeepSeek → 智谱。后说的能看到前面所有人说过的话。",
            font=("Microsoft YaHei", 9),
            foreground="gray",
        ).pack(fill="x", padx=15, pady=(0, 8))

    # ---------------- 工具 ----------------
    def log_message(self, target_text, header, content):
        target_text.insert(tk.END, f"=== {header} ===\n\n{content}\n\n")
        target_text.insert(tk.END, "-" * 40 + "\n\n")
        target_text.see(tk.END)

    def _build_messages(self, sys_prompt):
        """构造某家发言时的完整上下文：system + 共享历史（带说话人标签）"""
        messages = [{"role": "system", "content": sys_prompt}]
        for speaker, content in self.shared_history[-self.max_history:]:
            if speaker == "你":
                messages.append({"role": "user", "content": content})
            else:
                messages.append({"role": "user", "content": f"[{speaker} 刚刚说] {content}"})
        return messages

    def _chat(self, client, model, messages, temperature=0.8):
        resp = client.chat.completions.create(
            model=model, messages=messages, temperature=temperature
        )
        return resp.choices[0].message.content

    # ---------------- 核心 ----------------
    def send_message(self):
        if self.is_running:
            return
        text = self.entry.get("1.0", tk.END).strip()
        if not text:
            return

        self.entry.delete("1.0", tk.END)
        self.is_running = True
        self.btn_send.config(state="disabled")
        self.lbl_status.config(text="状态: 三家正在接龙...")

        # 你这句话进共享历史
        self.shared_history.append(("你", text))
        # 三个框都显示你说的话
        for txt in (self.txt_qwen, self.txt_ds, self.txt_zhipu):
            self.log_message(txt, "你", text)

        threading.Thread(target=self._run_chain, daemon=True).start()

    def _run_chain(self):
        try:
            # 1. Qwen 先说
            self.root.after(0, lambda: self.lbl_status.config(text="状态: Qwen 正在说..."))
            msgs = self._build_messages(SYS_QWEN)
            reply_qwen = self._chat(self.qwen_client, QWEN_MODEL, msgs)
            self.shared_history.append(("Qwen", reply_qwen))
            self.root.after(0, self.log_message, self.txt_qwen, "Qwen", reply_qwen)

            # 2. DeepSeek 接
            self.root.after(0, lambda: self.lbl_status.config(text="状态: DeepSeek 正在接话..."))
            msgs = self._build_messages(SYS_DS)
            reply_ds = self._chat(self.ds_client, DEEPSEEK_MODEL, msgs)
            self.shared_history.append(("DeepSeek", reply_ds))
            self.root.after(0, self.log_message, self.txt_ds, "DeepSeek", reply_ds)

            # 3. 智谱 收尾
            self.root.after(0, lambda: self.lbl_status.config(text="状态: 智谱 正在接话..."))
            msgs = self._build_messages(SYS_ZHIPU)
            reply_zhipu = self._chat(self.zhipu_client, ZHIPU_MODEL, msgs)
            self.shared_history.append(("智谱", reply_zhipu))
            self.root.after(0, self.log_message, self.txt_zhipu, "智谱", reply_zhipu)

            self.root.after(0, self._on_done)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("运行错误", str(e)))
            self.root.after(0, self._on_done)

    def _on_done(self):
        self.is_running = False
        self.btn_send.config(state="normal")
        self.lbl_status.config(text="状态: 就绪，继续输入")
        self.entry.focus_set()

    def clear_all(self):
        if self.is_running:
            messagebox.showinfo("请稍等", "三家还在接龙中，等说完再清空。")
            return
        self.shared_history = []
        self.txt_qwen.delete("1.0", tk.END)
        self.txt_ds.delete("1.0", tk.END)
        self.txt_zhipu.delete("1.0", tk.END)
        self.lbl_status.config(text="状态: 已清空，重新开始。")


if __name__ == "__main__":
    root = tk.Tk()
    app = AIChatGUI(root)
    root.mainloop()