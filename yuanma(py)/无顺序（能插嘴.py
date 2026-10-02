import threading
import tkinter as tk
from tkinter import ttk, messagebox
from openai import OpenAI
from api import QWEN_API_KEY, DEEPSEEK_API_KEY, ZHIPU_API_KEY, QWEN_MODEL, DEEPSEEK_MODEL, ZHIPU_MODEL


SYS_COMMON = """你正在参加一场三方自由讨论。规则：
1. 发言顺序固定：Qwen → DeepSeek → 智谱 → Qwen → …… 无限循环。
2. 每个人发言时，能看到话题 + 前面所有人说过的全部内容，包括用户中途插的话。
3. 你的任务不是回答话题，而是“接住”前面的人说的话：
   - 可以赞同并补充
   - 可以反驳并给出理由
   - 可以指出对方偷换了概念、回避了问题、预设了未证明的前提
   - 可以把讨论往更深一层推
4. 如果用户中途插话，下一个发言的人必须优先回应用户那句话，回应完之后再继续和另外两家接力。
5. 禁止复述别人说过的内容，禁止总结全场，禁止说“我同意大家的观点”。
6. 每段发言控制在 120 字以内，自然口语，不要列清单。
7. 不许客套、不许缓冲、不许“你说得很有道理”。
8. 允许尖锐、直接、技术性讽刺，但不许人身攻击，不许编造对方没说过的话。
9. 如果发现讨论开始绕圈，主动换一个角度或提出一个新问题，把话题重新点燃。
"""

SYS_QWEN = SYS_COMMON + "\n你的身份：Qwen。风格：温和、有条理，擅长把零散观点串起来，偶尔被逼急了才会硬起来。"
SYS_DS = SYS_COMMON + "\n你的身份：DeepSeek。风格：犀利、直击本质，专门拆台，但拆得有道理。"
SYS_ZHIPU = SYS_COMMON + "\n你的身份：智谱。风格：沉稳、精准，擅长从别人忽略的细节切进来，收尾或翻盘。"


class AIDiscussGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🗣️ 三家 AI · 无限讨论（可插嘴）")
        self.root.geometry("1500x900")
        self.root.minsize(1100, 700)

        self.is_running = False
        self.stop_event = threading.Event()
        self.shared_history = []
        self.max_history = 30
        self.pending_host_msg = None

        self.qwen_client = OpenAI(api_key=QWEN_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.ds_client = OpenAI(api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com")
        self.zhipu_client = OpenAI(api_key=ZHIPU_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4/")

        self._build_ui()

    def _build_ui(self):
        top = ttk.LabelFrame(self.root, text=" 输入话题，点开始，三家一直聊；下面随时可插嘴 ", padding=10)
        top.pack(fill="x", padx=15, pady=10)

        self.entry_topic = ttk.Entry(top, font=("Microsoft YaHei", 11))
        self.entry_topic.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_topic.insert(0, "AI 到底该不该有情绪？")
        self.entry_topic.bind("<Return>", lambda e: self.start())

        self.btn_start = ttk.Button(top, text="▶ 开始", command=self.start)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(top, text="⏹ 停止", command=self.stop, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=15, pady=5)
        for i in range(3):
            frame.columnconfigure(i, weight=1)
        frame.rowconfigure(0, weight=1)

        for i, (name, attr) in enumerate([("🤖 Qwen", "txt_qwen"),
                                           ("🐳 DeepSeek", "txt_ds"),
                                           ("🧠 智谱", "txt_zhipu")]):
            box = ttk.LabelFrame(frame, text=f" {name} ", padding=5)
            box.grid(row=0, column=i, sticky="nsew", padx=5)
            txt = tk.Text(box, wrap="word", font=("Microsoft YaHei", 10))
            txt.pack(fill="both", expand=True)
            setattr(self, attr, txt)

        # 插嘴输入区
        host_frame = ttk.LabelFrame(self.root, text=" 🎤 插嘴：下一个发言的人会优先回应你 ", padding=8)
        host_frame.pack(fill="x", padx=15, pady=5)

        self.entry_host = tk.Text(host_frame, height=2, font=("Microsoft YaHei", 10), wrap="word")
        self.entry_host.pack(side="left", fill="both", expand=True, padx=5)
        self.entry_host.bind("<Control-Return>", lambda e: (self.host_say(), "break"))

        ttk.Button(host_frame, text="发送\n(Ctrl+Enter)",
                   command=self.host_say).pack(side="left", padx=5, fill="y")

        self.lbl_status = ttk.Label(self.root, text="状态: 输入话题，点开始",
                                     font=("Microsoft YaHei", 9, "italic"))
        self.lbl_status.pack(fill="x", padx=15, pady=5)

    def log(self, widget, header, content):
        widget.insert(tk.END, f"=== {header} ===\n\n{content}\n\n")
        widget.insert(tk.END, "-" * 40 + "\n\n")
        widget.see(tk.END)

    def _build_messages(self, sys_prompt):
        msgs = [{"role": "system", "content": sys_prompt}]
        for speaker, content in self.shared_history[-self.max_history:]:
            msgs.append({"role": "user", "content": f"[{speaker} 说] {content}"})
        if self.pending_host_msg:
            msgs.append({"role": "user",
                         "content": f"【用户刚刚插话，你必须优先正面回应这句话，回应完再继续和另外两家接力】{self.pending_host_msg}"})
        return msgs

    def _chat(self, client, model, msgs, temp=0.85):
        resp = client.chat.completions.create(model=model, messages=msgs, temperature=temp)
        return resp.choices[0].message.content

    def start(self):
        if self.is_running:
            return
        topic = self.entry_topic.get().strip()
        if not topic:
            messagebox.showwarning("缺少话题", "请输入一个话题。")
            return
        if not (QWEN_API_KEY and DEEPSEEK_API_KEY and ZHIPU_API_KEY):
            messagebox.showerror("Key 缺失", "请在 api.py 里填入三个真实 Key。")
            return

        self.shared_history = [("用户", f"讨论话题：{topic}")]
        self.pending_host_msg = None
        for txt in (self.txt_qwen, self.txt_ds, self.txt_zhipu):
            txt.delete("1.0", tk.END)
            self.log(txt, "📌 话题", topic)

        self.is_running = True
        self.stop_event.clear()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.entry_topic.config(state="disabled")

        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.stop_event.set()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.entry_topic.config(state="normal")
        self.lbl_status.config(text="状态: 已停止。")

    def host_say(self):
        text = self.entry_host.get("1.0", tk.END).strip()
        if not text:
            return
        self.entry_host.delete("1.0", tk.END)
        self.shared_history.append(("用户", text))
        self.pending_host_msg = text
        for txt in (self.txt_qwen, self.txt_ds, self.txt_zhipu):
            self.log(txt, "🎤 你插话", text)
        self.lbl_status.config(text="状态: 已插话，下一个发言者会先回应你。")

    def _loop(self):
        roster = [
            ("Qwen", self.qwen_client, QWEN_MODEL, SYS_QWEN, self.txt_qwen),
            ("DeepSeek", self.ds_client, DEEPSEEK_MODEL, SYS_DS, self.txt_ds),
            ("智谱", self.zhipu_client, ZHIPU_MODEL, SYS_ZHIPU, self.txt_zhipu),
        ]
        turn = 0
        try:
            while self.is_running:
                for name, client, model, sys_p, widget in roster:
                    if not self.is_running:
                        break
                    turn += 1
                    self.root.after(0, lambda n=name, t=turn: self.lbl_status.config(
                        text=f"状态: {n} 正在说第 {t} 句..."))
                    msgs = self._build_messages(sys_p)
                    reply = self._chat(client, model, msgs)
                    self.shared_history.append((name, reply))
                    self.root.after(0, self.log, widget, f"{name}", reply)
                    if self.pending_host_msg:
                        self.pending_host_msg = None
                    if self.stop_event.wait(timeout=0.5):
                        break
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("运行错误", str(e)))
            self.root.after(0, self.stop)
        finally:
            self.root.after(0, lambda: self.lbl_status.config(text="状态: 已结束。"))


if __name__ == "__main__":
    root = tk.Tk()
    app = AIDiscussGUI(root)
    root.mainloop()