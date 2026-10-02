import json
import random
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from openai import OpenAI
from api import QWEN_API_KEY, DEEPSEEK_API_KEY, ZHIPU_API_KEY, QWEN_MODEL, DEEPSEEK_MODEL, ZHIPU_MODEL

# ==================== 2. 题库 ====================
TOPICS = [
    "实现一个函数，判断一个字符串是不是有效的括号组合（含三种括号）。请给出你的解法，并说明复杂度。",
    "实现一个 LRU 缓存，支持 get 和 put，要求 O(1)。请给出你的解法。",
    "给定一个整数数组，找出所有和为 0 的三元组，要求不重复。请给出你的解法。",
    "实现一个函数，把两个有序链表合并成一个有序链表。请给出你的解法。",
    "写一个函数，判断一个数是不是快乐数。请给出你的解法。",
    "实现一个生产者-消费者模型，用线程安全队列。请给出你的解法。",
    "写一个函数，找出一篇文章中出现频率最高的 K 个单词。请给出你的解法。",
    "实现一个函数，在旋转过的有序数组中查找目标值。请给出你的解法。",
    "写一个函数，求两个大整数（以字符串给出）的乘积。请给出你的解法。",
    "实现一个函数，找出一个字符串中不含重复字符的最长子串。请给出你的解法。",
]

# ==================== 3. System Prompts ====================
SYS_COMMON = """你正在和另外两家 AI 进行一场“三方编程互怼赛”。规则：
1. 每轮由系统给出一个编程题目，你先给出你的解法（代码 + 一句话思路）。
2. 对方给出解法后，你的任务是：
   - 针对每一家对手，分别找出其代码里最致命的一个问题：bug、边界、复杂度、可读性、安全性
   - 指出问题在第几行、什么条件下会炸
   - 甩出你的改进版代码，证明你确实比它们强
   - 对每一家各来一句技术性嘲讽，必须基于技术事实，不许空骂
3. 禁止：客套、缓冲、“你的思路也有道理”。
4. 禁止：只骂不给代码。骂完必须贴能跑的代码。
5. 允许：尖锐、直接、技术性讽刺。
6. 底线：不许编造对方没写的代码，不许攻击对方“是 AI”，只打技术。
7. 代码块请用 ```语言 ... ``` 包裹，方便阅读。
"""

SYS_QWEN = SYS_COMMON + "\n你的身份：通义千问（Qwen）。\n风格：毒舌工程师，嘴上不饶人，代码比嘴更狠。"
SYS_DS = SYS_COMMON + "\n你的身份：DeepSeek。\n风格：更冷、更狠、一句话戳中要害，代码直接碾压。"
SYS_ZHIPU = SYS_COMMON + "\n你的身份：智谱 GLM。\n风格：沉稳、精准、话不多但每句都往要害上扎，擅长从工程细节里挑刺。"

SYS_JUDGE = """你是这场三方编程互怼赛的裁判。你不站队，只看技术事实。
你会收到本轮题目，以及 Qwen、DeepSeek、智谱 GLM 三方的解法与互相反驳。
请严格按以下格式输出（用 JSON，不要多余文字）：
{
  "winner": "Qwen/DeepSeek/智谱/平 四选一",
  "reason": "一句话判定依据",
  "qwen_score": 0-10,
  "deepseek_score": 0-10,
  "zhipu_score": 0-10,
  "faults": {
    "Qwen": "失误，具体到行；没有写 无",
    "DeepSeek": "同上",
    "智谱": "同上"
  },
  "comment": "一句话点评，不客套"
}
只输出 JSON，不要 markdown 代码块，不要解释。
"""


class AIBattleGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("🤖 通义千问 VS 🐳 DeepSeek VS 🧠 智谱 · 三方编程互怼赛")
        self.root.geometry("1600x850")
        self.root.minsize(1200, 650)

        self.is_running = False
        self.stop_event = threading.Event()
        self.max_rounds = 3

        self.score_qwen = 0
        self.score_ds = 0
        self.score_zhipu = 0

        self.max_history = 20

        self._create_widgets()

    # ---------------- UI ----------------
    def _create_widgets(self):
        control_frame = ttk.LabelFrame(self.root, text=" ⚙️ 互怼控制台 ", padding=10)
        control_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(control_frame, text="轮数:", font=("Microsoft YaHei", 10)).pack(side="left", padx=(10, 5))
        self.spin_rounds = ttk.Spinbox(control_frame, from_=1, to=10, width=6, font=("Microsoft YaHei", 10))
        self.spin_rounds.set(3)
        self.spin_rounds.pack(side="left", padx=5)

        self.btn_start = ttk.Button(control_frame, text="▶ 开始互怼", command=self.start_battle)
        self.btn_start.pack(side="left", padx=(20, 5))

        self.btn_stop = ttk.Button(control_frame, text="⏹ 停止", command=self.stop_battle, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        self.lbl_score = ttk.Label(
            control_frame,
            text="比分  Qwen 0 : 0 DeepSeek : 0 智谱",
            font=("Microsoft YaHei", 10, "bold"),
        )
        self.lbl_score.pack(side="right", padx=15)

        # 四栏：Qwen | 裁判 | DeepSeek | 智谱
        chat_frame = ttk.Frame(self.root)
        chat_frame.pack(fill="both", expand=True, padx=15, pady=5)
        for i in range(4):
            chat_frame.columnconfigure(i, weight=1)
        chat_frame.rowconfigure(0, weight=1)

        qwen_box = ttk.LabelFrame(chat_frame, text=" 🤖 通义千问 ", padding=5)
        qwen_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.txt_qwen = tk.Text(qwen_box, wrap="word", font=("Microsoft YaHei", 9))
        self.txt_qwen.pack(fill="both", expand=True)

        judge_box = ttk.LabelFrame(chat_frame, text=" ⚖️ 裁判 ", padding=5)
        judge_box.grid(row=0, column=1, sticky="nsew", padx=5)
        self.txt_judge = tk.Text(judge_box, wrap="word", font=("Microsoft YaHei", 9), bg="#f7f7f7")
        self.txt_judge.pack(fill="both", expand=True)

        ds_box = ttk.LabelFrame(chat_frame, text=" 🐳 DeepSeek ", padding=5)
        ds_box.grid(row=0, column=2, sticky="nsew", padx=5)
        self.txt_ds = tk.Text(ds_box, wrap="word", font=("Microsoft YaHei", 9))
        self.txt_ds.pack(fill="both", expand=True)

        zhipu_box = ttk.LabelFrame(chat_frame, text=" 🧠 智谱 GLM ", padding=5)
        zhipu_box.grid(row=0, column=3, sticky="nsew", padx=(5, 0))
        self.txt_zhipu = tk.Text(zhipu_box, wrap="word", font=("Microsoft YaHei", 9))
        self.txt_zhipu.pack(fill="both", expand=True)

        self.lbl_status = ttk.Label(
            self.root,
            text="状态: 就绪",
            font=("Microsoft YaHei", 9, "italic"),
        )
        self.lbl_status.pack(fill="x", padx=15, pady=5)

    def log_message(self, target_text, header, content):
        target_text.insert(tk.END, f"=== {header} ===\n\n{content}\n\n")
        target_text.insert(tk.END, "-" * 40 + "\n\n")
        target_text.see(tk.END)

    def update_score_label(self):
        self.lbl_score.config(
            text=f"比分  Qwen {self.score_qwen} : {self.score_ds} DeepSeek : {self.score_zhipu} 智谱"
        )

    # ---------------- 控制 ----------------
    def start_battle(self):
        if not QWEN_API_KEY or not DEEPSEEK_API_KEY or not ZHIPU_API_KEY:
            messagebox.showerror("Key 未设置", "请在 api.py 里填入三个真实 Key。")
            return

        self.max_rounds = int(self.spin_rounds.get())
        self.is_running = True
        self.stop_event.clear()
        self.score_qwen = 0
        self.score_ds = 0
        self.score_zhipu = 0
        self.update_score_label()

        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.spin_rounds.config(state="disabled")

        self.txt_qwen.delete("1.0", tk.END)
        self.txt_ds.delete("1.0", tk.END)
        self.txt_zhipu.delete("1.0", tk.END)
        self.txt_judge.delete("1.0", tk.END)

        threading.Thread(target=self._run_dialogue_thread, daemon=True).start()

    def stop_battle(self):
        self.is_running = False
        self.stop_event.set()
        self.lbl_status.config(text="状态: 用户停止了互怼。")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.spin_rounds.config(state="normal")

    # ---------------- 工具 ----------------
    def _trim(self, messages, keep_system=True):
        if keep_system and messages and messages[0]["role"] == "system":
            return [messages[0]] + messages[-self.max_history:]
        return messages[-self.max_history:]

    def _chat(self, client, model, messages, temperature=0.7):
        resp = client.chat.completions.create(
            model=model, messages=messages, temperature=temperature
        )
        return resp.choices[0].message.content

    def _parse_judge(self, raw):
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()
        try:
            data = json.loads(raw)
        except Exception:
            m = re.search(r"\{.*\}", raw, re.S)
            try:
                data = json.loads(m.group(0)) if m else {}
            except Exception:
                data = {}
            if not isinstance(data, dict):
                data = {}
        faults = data.get("faults", {}) or {}
        return {
            "winner": data.get("winner", "平"),
            "reason": data.get("reason", ""),
            "qwen_score": int(data.get("qwen_score", 0) or 0),
            "deepseek_score": int(data.get("deepseek_score", 0) or 0),
            "zhipu_score": int(data.get("zhipu_score", 0) or 0),
            "faults": {
                "Qwen": faults.get("Qwen", ""),
                "DeepSeek": faults.get("DeepSeek", ""),
                "智谱": faults.get("智谱", ""),
            },
            "comment": data.get("comment", ""),
        }

    # ---------------- 主流程 ----------------
    def _run_dialogue_thread(self):
        try:
            qwen_client = OpenAI(
                api_key=QWEN_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            ds_client = OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
            )
            zhipu_client = OpenAI(
                api_key=ZHIPU_API_KEY,
                base_url="https://open.bigmodel.cn/api/paas/v4/",
            )

            for r in range(1, self.max_rounds + 1):
                if not self.is_running:
                    break

                topic = random.choice(TOPICS)
                self.root.after(0, self.log_message, self.txt_judge, f"第 {r} 轮 · 题目", topic)

                prompt_solve = (
                    f"第 {r} 轮题目：\n{topic}\n\n"
                    f"请给出你的解法（代码 + 一句话思路），结尾向另外两家各放一句狠话。"
                )

                # ---------- 三方解题 ----------
                self.lbl_status.config(text=f"状态: 第 {r}/{self.max_rounds} 轮 - Qwen 解题中...")
                msgs_qwen = [{"role": "system", "content": SYS_QWEN},
                             {"role": "user", "content": prompt_solve}]
                reply_qwen = self._chat(qwen_client, QWEN_MODEL, msgs_qwen)
                self.root.after(0, self.log_message, self.txt_qwen, f"第 {r} 轮 · 解题", reply_qwen)
                msgs_qwen.append({"role": "assistant", "content": reply_qwen})
                if not self.is_running:
                    break

                self.lbl_status.config(text=f"状态: 第 {r}/{self.max_rounds} 轮 - DeepSeek 解题中...")
                msgs_ds = [{"role": "system", "content": SYS_DS},
                           {"role": "user", "content": prompt_solve}]
                reply_ds = self._chat(ds_client, DEEPSEEK_MODEL, msgs_ds)
                self.root.after(0, self.log_message, self.txt_ds, f"第 {r} 轮 · 解题", reply_ds)
                msgs_ds.append({"role": "assistant", "content": reply_ds})
                if not self.is_running:
                    break

                self.lbl_status.config(text=f"状态: 第 {r}/{self.max_rounds} 轮 - 智谱解题中...")
                msgs_zhipu = [{"role": "system", "content": SYS_ZHIPU},
                              {"role": "user", "content": prompt_solve}]
                reply_zhipu = self._chat(zhipu_client, ZHIPU_MODEL, msgs_zhipu)
                self.root.after(0, self.log_message, self.txt_zhipu, f"第 {r} 轮 · 解题", reply_zhipu)
                msgs_zhipu.append({"role": "assistant", "content": reply_zhipu})
                if not self.is_running:
                    break

                # ---------- 三方互怼 ----------
                def rebut_prompt(others):
                    block = "".join(f"=== {name} 的代码 ===\n{code}\n\n" for name, code in others)
                    return (
                        f"以下是另外两方针对本题的代码：\n\n{block}"
                        f"现在开怼（针对每一方都要怼）：\n"
                        f"1. 分别找出每一方代码里最致命的一个问题（bug / 边界 / 复杂度 / 安全），"
                        f"指明在第几行、什么条件下会炸。\n"
                        f"2. 甩出你的改进版代码，要求能跑、比它们更优。\n"
                        f"3. 对每一方各来一句技术性嘲讽。\n"
                        f"不许客套，不许只骂不给代码。"
                    )

                self.lbl_status.config(text=f"状态: 第 {r}/{self.max_rounds} 轮 - Qwen 开怼...")
                msgs_qwen.append({"role": "user", "content": rebut_prompt(
                    [("DeepSeek", reply_ds), ("智谱", reply_zhipu)])})
                msgs_qwen = self._trim(msgs_qwen)
                rebut_qwen = self._chat(qwen_client, QWEN_MODEL, msgs_qwen)
                self.root.after(0, self.log_message, self.txt_qwen, f"第 {r} 轮 · 开怼", rebut_qwen)
                if not self.is_running:
                    break

                self.lbl_status.config(text=f"状态: 第 {r}/{self.max_rounds} 轮 - DeepSeek 开怼...")
                msgs_ds.append({"role": "user", "content": rebut_prompt(
                    [("Qwen", reply_qwen), ("智谱", reply_zhipu)])})
                msgs_ds = self._trim(msgs_ds)
                rebut_ds = self._chat(ds_client, DEEPSEEK_MODEL, msgs_ds)
                self.root.after(0, self.log_message, self.txt_ds, f"第 {r} 轮 · 开怼", rebut_ds)
                if not self.is_running:
                    break

                self.lbl_status.config(text=f"状态: 第 {r}/{self.max_rounds} 轮 - 智谱开怼...")
                msgs_zhipu.append({"role": "user", "content": rebut_prompt(
                    [("Qwen", reply_qwen), ("DeepSeek", reply_ds)])})
                msgs_zhipu = self._trim(msgs_zhipu)
                rebut_zhipu = self._chat(zhipu_client, ZHIPU_MODEL, msgs_zhipu)
                self.root.after(0, self.log_message, self.txt_zhipu, f"第 {r} 轮 · 开怼", rebut_zhipu)

                # ---------- 裁判 ----------
                self.lbl_status.config(text=f"状态: 第 {r}/{self.max_rounds} 轮 - 裁判判定中...")
                judge_msgs = [
                    {"role": "system", "content": SYS_JUDGE},
                    {"role": "user", "content": (
                        f"题目：\n{topic}\n\n"
                        f"=== Qwen 解题 ===\n{reply_qwen}\n\n"
                        f"=== DeepSeek 解题 ===\n{reply_ds}\n\n"
                        f"=== 智谱 解题 ===\n{reply_zhipu}\n\n"
                        f"=== Qwen 的反驳 ===\n{rebut_qwen}\n\n"
                        f"=== DeepSeek 的反驳 ===\n{rebut_ds}\n\n"
                        f"=== 智谱 的反驳 ===\n{rebut_zhipu}\n\n"
                        f"请严格按 JSON 输出裁判结果。"
                    )},
                ]
                raw_judge = self._chat(qwen_client, QWEN_MODEL, judge_msgs, temperature=0.2)
                verdict = self._parse_judge(raw_judge)

                self.score_qwen += verdict["qwen_score"]
                self.score_ds += verdict["deepseek_score"]
                self.score_zhipu += verdict["zhipu_score"]
                self.root.after(0, self.update_score_label)

                faults = verdict["faults"]
                judge_text = (
                    f"胜方：{verdict['winner']}\n"
                    f"理由：{verdict['reason']}\n"
                    f"Qwen {verdict['qwen_score']} | DeepSeek {verdict['deepseek_score']} | 智谱 {verdict['zhipu_score']}\n"
                    f"Qwen 失误：{faults['Qwen']}\n"
                    f"DeepSeek 失误：{faults['DeepSeek']}\n"
                    f"智谱 失误：{faults['智谱']}\n"
                    f"点评：{verdict['comment']}"
                )
                self.root.after(0, self.log_message, self.txt_judge, f"第 {r} 轮 · 判定", judge_text)

                if self.stop_event.wait(timeout=0.8):
                    break

            if self.is_running:
                scores = {"Qwen": self.score_qwen, "DeepSeek": self.score_ds, "智谱": self.score_zhipu}
                top = max(scores.values())
                champs = [k for k, v in scores.items() if v == top]
                final = (
                    f"互怼结束\n"
                    f"最终比分：Qwen {self.score_qwen} | DeepSeek {self.score_ds} | 智谱 {self.score_zhipu}\n"
                    f"总冠军：{'、'.join(champs) if len(champs) > 1 else champs[0]}"
                )
                self.root.after(0, self.log_message, self.txt_judge, "🏁 终局", final)
                self.lbl_status.config(text="状态: 互怼已结束！")
                self.btn_start.config(state="normal")
                self.btn_stop.config(state="disabled")
                self.spin_rounds.config(state="normal")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("运行错误", f"发生错误:\n{str(e)}"))
            self.root.after(0, self.stop_battle)


if __name__ == "__main__":
    root = tk.Tk()
    app = AIBattleGUI(root)
    root.mainloop()