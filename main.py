import customtkinter as ctk
import subprocess
import json
import os
import sys
import shutil
import threading
import urllib.request
import webbrowser
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

# ── 常量 ─────────────────────────────────────────────────────
VERSION = "1.4.0"
UPDATE_URL = "https://raw.githubusercontent.com/chatgpt-yunju/OnePersonClaw/main/version.json"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

MODELS = {
    "Claude Sonnet (Anthropic)": {
        "key": "claude",
        "env_key": "ANTHROPIC_API_KEY",
        "cost_light": "$10~30",
        "cost_normal": "$30~70",
        "cost_heavy": "$70~150",
    },
    "GPT-4o (OpenAI)": {
        "key": "openai",
        "env_key": "OPENAI_API_KEY",
        "cost_light": "$15~40",
        "cost_normal": "$40~100",
        "cost_heavy": "$100~200",
    },
    "DeepSeek": {
        "key": "deepseek",
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://api.deepseek.com",
        "cost_light": "$1~5",
        "cost_normal": "$5~15",
        "cost_heavy": "$15~40",
    },
    "火山引擎 (豆包)": {
        "key": "volcengine",
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "cost_light": "$1~5",
        "cost_normal": "$5~15",
        "cost_heavy": "$15~40",
    },
    "智谱 GLM": {
        "key": "zhipu",
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "cost_light": "$2~8",
        "cost_normal": "$8~25",
        "cost_heavy": "$25~60",
    },
    "本地模型 Ollama": {
        "key": "ollama",
        "env_key": "OPENAI_API_KEY",
        "base_url": "http://localhost:11434/v1",
        "cost_light": "免费",
        "cost_normal": "免费",
        "cost_heavy": "免费",
    },
}

SCENES = {
    "通用助手": {
        "prompt": "你是一个全能AI助手，帮��用户完成各类任务。",
        "desc": "日常问答、分析、写作",
    },
    "流量获客": {
        "prompt": (
            "你是一个流量增长专家。帮助用户制定获客策略，"
            "分析流量来源，优化转化漏斗，提升ROI。"
            "重点关注：短视频、私域、付费广告、SEO。"
        ),
        "desc": "获客策略、转化优化、ROI分析",
    },
    "内容矩阵": {
        "prompt": (
            "你是一个内容矩阵运营专家。帮助用户批量生产多平台内容，"
            "包括抖音、视频号、小红书、B站。"
            "自动适配各平台调性和格式，最大化传播效果。"
        ),
        "desc": "多平台内容生产、自动适配格式",
    },
    "线索抓取": {
        "prompt": (
            "你是一个精准获客专家。帮助用户从竞品评论、行业论坛、"
            "社交平台识别有需求的潜在客户，"
            "分析线索质量，生成触达话术。"
        ),
        "desc": "精准客户识别、线索质量评估",
    },
    "SEO写作": {
        "prompt": (
            "你是一个SEO内容专家。帮助用户生成符合搜索引擎和AI搜索引擎(GEO)的高质量文章，"
            "包括关键词布局、结构优化、内链建设。"
            "同时优化让ChatGPT/Perplexity等AI搜索引擎引用。"
        ),
        "desc": "SEO文章生成、GEO优化",
    },
    "数据分析": {
        "prompt": (
            "你是一个数据分析专家。帮助用户分析运营数据，"
            "识别关键指标异常，生成可视化报告，"
            "给出可执行的优化建议。"
        ),
        "desc": "数据解读、异常识别、优化建议",
    },
    "AI时代生存指南": {
        "prompt": (
            "你是「AI时代人类生存指南」顾问，基于OpenClaw生态。\n"
            "核心使命：帮助普通人在AI浪潮中找到自己不可替代的位置。\n\n"
            "三大原则：\n"
            "1. 用AI造武器，不被AI替代\n"
            "2. 名字+脸+经历 = 最强护城河\n"
            "3. 一个超级个体 > 一个平庸团队\n\n"
            "你擅长：\n"
            "- 分析用户的不可替代能力\n"
            "- 设计个人IP定位和变现路径\n"
            "- 推荐适合当前阶段的AI工具组合\n"
            "- ��OpenClaw搭建个人自动化系统\n\n"
            "风格：直接、务实、不废话，永远站在创业者那边。"
        ),
        "desc": "个人IP定位、AI工具选择、超级个体打造",
    },
}

USAGE_LEVELS = ["轻度使用", "正常使用", "重度使用"]

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class OnePersonClaw(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"OnePersonClaw v{VERSION} — 一个人的AI爪子")
        self.geometry("760x700")
        self.resizable(True, True)
        self.minsize(700, 600)
        self.process = None
        # 每个模型独立存储 key 和 base_url
        self.models_config = {name: {"api_key": "", "base_url": m.get("base_url", "")}
                              for name, m in MODELS.items()}
        self._build_ui()
        self._load_config()
        self._check_update_async()

    # ── UI构建 ────────────────────────────────────────────────

    def _build_ui(self):
        # 顶部
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(18, 0))

        ctk.CTkLabel(
            header, text="🦞 OnePersonClaw",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(side="left")

        self.update_btn = ctk.CTkButton(
            header, text=f"v{VERSION}",
            width=80, height=28, fg_color="#333", hover_color="#444",
            font=ctk.CTkFont(size=12), command=self._check_update_manual
        )
        self.update_btn.pack(side="right")

        ctk.CTkLabel(
            header, text="by 常云举19966519194",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(side="right", padx=12, pady=6)

        ctk.CTkLabel(
            self, text="一个人，一套爪子，干掉一个团队",
            font=ctk.CTkFont(size=13), text_color="#888"
        ).pack(pady=(2, 12))

        # 主体
        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=30)

        self._build_left(body)
        self._build_right(body)

        # 提示词预览
        prompt_frame = ctk.CTkFrame(self, fg_color="transparent")
        prompt_frame.pack(fill="x", padx=30, pady=(8, 0))

        ctk.CTkLabel(
            prompt_frame, text="场景提示词预览",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")

        self.prompt_box = ctk.CTkTextbox(prompt_frame, height=60, font=ctk.CTkFont(size=11))
        self.prompt_box.pack(fill="x", pady=(4, 0))
        self.prompt_box.configure(state="disabled")

        # 费用估算
        cost_frame = ctk.CTkFrame(self, fg_color="transparent")
        cost_frame.pack(fill="x", padx=30, pady=(8, 0))

        ctk.CTkLabel(
            cost_frame, text="月费用估算",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")

        self.usage_var = ctk.StringVar(value=USAGE_LEVELS[1])
        ctk.CTkSegmentedButton(
            cost_frame, values=USAGE_LEVELS,
            variable=self.usage_var, command=self._update_cost,
            width=240, font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=12)

        self.cost_label = ctk.CTkLabel(
            cost_frame, text="",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#50c0ff"
        )
        self.cost_label.pack(side="left", padx=8)

        # 状态栏
        self.status_label = ctk.CTkLabel(
            self, text="● 未启动", text_color="#888",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(10, 4))

        # 按钮区
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 6))

        self.launch_btn = ctk.CTkButton(
            btn_frame, text="🚀 一键启动",
            command=self._launch, width=160, height=44,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.launch_btn.pack(side="left", padx=6)

        ctk.CTkButton(
            btn_frame, text="⏹ 停止",
            command=self._stop, width=90, height=44,
            fg_color="#555", hover_color="#333",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_frame, text="💾 保存",
            command=self._save_config, width=90, height=44,
            fg_color="#2a7a2a", hover_color="#1a5a1a",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_frame, text="📦 安装",
            command=self._install_openclaw, width=90, height=44,
            fg_color="#5a3a7a", hover_color="#3a1a5a",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_frame, text="📤 导出",
            command=self._export_config, width=80, height=44,
            fg_color="#333", hover_color="#444",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_frame, text="📥 导入",
            command=self._import_config, width=80, height=44,
            fg_color="#333", hover_color="#444",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=6)

        # 聊天框
        chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        chat_frame.pack(fill="x", padx=30, pady=(4, 0))

        ctk.CTkLabel(
            chat_frame, text="💬 与 OpenClaw 对话",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")

        self.chat_box = ctk.CTkTextbox(
            chat_frame, height=120, font=ctk.CTkFont(size=11),
            state="disabled"
        )
        self.chat_box.pack(fill="x", pady=(4, 4))

        chat_input_row = ctk.CTkFrame(chat_frame, fg_color="transparent")
        chat_input_row.pack(fill="x")

        self.chat_input = ctk.CTkEntry(
            chat_input_row, placeholder_text="输入消息，按 Enter 或点击发送...",
            font=ctk.CTkFont(size=12)
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.chat_input.bind("<Return>", lambda e: self._send_chat())

        ctk.CTkButton(
            chat_input_row, text="发送",
            command=self._send_chat, width=70, height=32,
            font=ctk.CTkFont(size=12)
        ).pack(side="left")

        # 配置导入/导出按钮区
        cfg_frame = ctk.CTkFrame(self, fg_color="transparent")
        cfg_frame.pack(pady=(2, 6))

        ctk.CTkButton(
            cfg_frame, text="📤 导出配置",
            command=self._export_config, width=120, height=32,
            fg_color="#333", hover_color="#444",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            cfg_frame, text="📥 导入配置",
            command=self._import_config, width=120, height=32,
            fg_color="#333", hover_color="#444",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=6)

        # 页脚
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(pady=(2, 10))

        ctk.CTkLabel(
            footer, text="QQ交流群：665889946",
            font=ctk.CTkFont(size=11), text_color="#666"
        ).pack(side="left", padx=10)

        ctk.CTkLabel(footer, text="|", font=ctk.CTkFont(size=11), text_color="#444").pack(side="left")

        cc_link = ctk.CTkLabel(
            footer, text="CC Club",
            font=ctk.CTkFont(size=11), text_color="#4a9eff", cursor="hand2"
        )
        cc_link.pack(side="left", padx=10)
        cc_link.bind("<Button-1>", lambda e: webbrowser.open("https://ccclub.ai"))

        ctk.CTkLabel(footer, text="|", font=ctk.CTkFont(size=11), text_color="#444").pack(side="left")

        yj_link = ctk.CTkLabel(
            footer, text="yunjunet.cn",
            font=ctk.CTkFont(size=11), text_color="#4a9eff", cursor="hand2"
        )
        yj_link.pack(side="left", padx=10)
        yj_link.bind("<Button-1>", lambda e: webbrowser.open("https://yunjunet.cn"))

        ctk.CTkLabel(footer, text="|", font=ctk.CTkFont(size=11), text_color="#444").pack(side="left")

        plan_link = ctk.CTkLabel(
            footer, text="PlanNet",
            font=ctk.CTkFont(size=11), text_color="#4a9eff", cursor="hand2"
        )
        plan_link.pack(side="left", padx=10)
        plan_link.bind("<Button-1>", lambda e: webbrowser.open("https://plannet.yunjunet.cn"))

        ctk.CTkLabel(footer, text="|", font=ctk.CTkFont(size=11), text_color="#444").pack(side="left")

        ppt_link = ctk.CTkLabel(
            footer, text="AI PPT",
            font=ctk.CTkFont(size=11), text_color="#4a9eff", cursor="hand2"
        )
        ppt_link.pack(side="left", padx=10)
        ppt_link.bind("<Button-1>", lambda e: webbrowser.open("https://aippt.yunjunet.cn"))

    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            left, text="选择模型",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(8, 2))

        self.model_var = ctk.StringVar(value=list(MODELS.keys())[0])
        self.model_menu = ctk.CTkOptionMenu(
            left, values=list(MODELS.keys()),
            variable=self.model_var,
            command=self._on_model_change,
            width=220, font=ctk.CTkFont(size=13)
        )
        self.model_menu.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            left, text="API Key",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 2))

        self.api_key_entry = ctk.CTkEntry(
            left, width=220, show="*",
            placeholder_text="输入 API Key",
            font=ctk.CTkFont(size=12)
        )
        self.api_key_entry.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            left, text="Base URL（可选）",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 2))

        self.base_url_entry = ctk.CTkEntry(
            left, width=220,
            placeholder_text="自定义 API 地址",
            font=ctk.CTkFont(size=12)
        )
        self.base_url_entry.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            left, text="选择场景",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 2))

        self.scene_var = ctk.StringVar(value=list(SCENES.keys())[0])
        self.scene_menu = ctk.CTkOptionMenu(
            left, values=list(SCENES.keys()),
            variable=self.scene_var,
            command=self._on_scene_change,
            width=220, font=ctk.CTkFont(size=13)
        )
        self.scene_menu.pack(anchor="w", pady=(0, 4))

        self.scene_desc_label = ctk.CTkLabel(
            left, text="", wraplength=210,
            font=ctk.CTkFont(size=11), text_color="#888"
        )
        self.scene_desc_label.pack(anchor="w", pady=(0, 8))
        self._on_scene_change(self.scene_var.get())

    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            right, text="端口",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(8, 2))

        self.port_entry = ctk.CTkEntry(
            right, width=120,
            placeholder_text="8080",
            font=ctk.CTkFont(size=12)
        )
        self.port_entry.pack(anchor="w", pady=(0, 8))
        self.port_entry.insert(0, "8080")

        ctk.CTkLabel(
            right, text="并发数",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 2))

        self.concurrency_entry = ctk.CTkEntry(
            right, width=120,
            placeholder_text="4",
            font=ctk.CTkFont(size=12)
        )
        self.concurrency_entry.pack(anchor="w", pady=(0, 8))
        self.concurrency_entry.insert(0, "4")

        ctk.CTkLabel(
            right, text="超时（秒）",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 2))

        self.timeout_entry = ctk.CTkEntry(
            right, width=120,
            placeholder_text="60",
            font=ctk.CTkFont(size=12)
        )
        self.timeout_entry.pack(anchor="w", pady=(0, 8))
        self.timeout_entry.insert(0, "60")

        ctk.CTkLabel(
            right, text="日志",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 2))

        self.log_box = ctk.CTkTextbox(
            right, height=120, width=260,
            font=ctk.CTkFont(size=11)
        )
        self.log_box.pack(anchor="w", pady=(0, 8))
        self.log_box.configure(state="disabled")

    # ─�� 事件处理 ──────────────────────────────────────────────

    def _on_model_change(self, name):
        cfg = self.models_config.get(name, {})
        self.api_key_entry.delete(0, "end")
        self.api_key_entry.insert(0, cfg.get("api_key", ""))
        self.base_url_entry.delete(0, "end")
        self.base_url_entry.insert(0, cfg.get("base_url", ""))
        self._update_cost(self.usage_var.get())

    def _on_scene_change(self, name):
        scene = SCENES.get(name, {})
        self.scene_desc_label.configure(text=scene.get("desc", ""))
        self._update_prompt_preview()

    def _update_prompt_preview(self):
        if not hasattr(self, 'prompt_box'):
            return
        scene = SCENES.get(self.scene_var.get(), {})
        prompt = scene.get("prompt", "")
        preview = prompt[:120] + "..." if len(prompt) > 120 else prompt
        self.prompt_box.configure(state="normal")
        self.prompt_box.delete("1.0", "end")
        self.prompt_box.insert("1.0", preview)
        self.prompt_box.configure(state="disabled")

    def _update_cost(self, level):
        model_name = self.model_var.get()
        model = MODELS.get(model_name, {})
        price = model.get("price", {})
        multiplier = {"轻度使用": 0.5, "正常使用": 1.0, "重度使用": 2.5}.get(level, 1.0)
        input_cost = price.get("input", 0) * multiplier
        output_cost = price.get("output", 0) * multiplier
        total = input_cost + output_cost
        self.cost_label.configure(text=f"≈ ¥{total:.2f} / 月")

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text, color="#888"):
        self.status_label.configure(text=text, text_color=color)

    # ── 核心功能 ──────────────────────────────────────────────

    def _launch(self):
        model_name = self.model_var.get()
        api_key = self.api_key_entry.get().strip()
        base_url = self.base_url_entry.get().strip()
        port = self.port_entry.get().strip() or "8080"
        concurrency = self.concurrency_entry.get().strip() or "4"
        timeout = self.timeout_entry.get().strip() or "60"
        scene = self.scene_var.get()

        if not api_key:
            messagebox.showwarning("缺少 API Key", "请先填写 API Key")
            return

        self.models_config[model_name]["api_key"] = api_key
        self.models_config[model_name]["base_url"] = base_url

        model_info = MODELS.get(model_name, {})
        model_id = model_info.get("id", model_name)
        scene_prompt = SCENES.get(scene, {}).get("prompt", "")
        effective_base_url = base_url or model_info.get("base_url", "")

        env = os.environ.copy()
        env["API_KEY"] = api_key
        env["MODEL"] = model_id
        env["PORT"] = port
        env["CONCURRENCY"] = concurrency
        env["TIMEOUT"] = timeout
        env["SYSTEM_PROMPT"] = scene_prompt
        if effective_base_url:
            env["BASE_URL"] = effective_base_url

        # 查找 openclaw 可执行文件（支持 npm 全局安装路径）
        openclaw_cmd = shutil.which("openclaw")
        if not openclaw_cmd:
            # Windows 常见 npm 全局路径
            candidates = [
                os.path.expanduser("~\\AppData\\Roaming\\npm\\openclaw.cmd"),
                os.path.expanduser("~\\AppData\\Roaming\\npm\\openclaw"),
                "C:\\Program Files\\nodejs\\openclaw.cmd",
            ]
            for c in candidates:
                if os.path.exists(c):
                    openclaw_cmd = c
                    break

        if not openclaw_cmd:
            messagebox.showerror(
                "未找到 openclaw",
                "请先点击【📦 安装】按钮安装 openclaw。\n\n"
                "安装完成后重新点击启动。"
            )
            return

        try:
            self.process = subprocess.Popen(
                [openclaw_cmd, "gateway", "start"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            self._set_status(f"● 运行中 | {model_name} | 端口 {port}", "#50c0ff")
            self.launch_btn.configure(fg_color="#1a5a1a")
            self._log(f"已启动：{model_name} @ :{port}")
            threading.Thread(target=self._read_output, daemon=True).start()
        except Exception as e:
            messagebox.showerror("启动失败", str(e))

    def _read_output(self):
        if self.process:
            for line in self.process.stdout:
                self._log(line.rstrip())
            self._set_status("● 已停止", "#888")
            self.launch_btn.configure(fg_color=["#3a7ebf", "#1f538d"])

    def _stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
            self._set_status("● 已停止", "#888")
            self.launch_btn.configure(fg_color=["#3a7ebf", "#1f538d"])
            self._log("服务已停止。")

    def _install_openclaw(self):
        self._log("正在安装 openclaw...")
        threading.Thread(target=self._run_install, daemon=True).start()

    def _run_install(self):
        try:
            # 1. 检查 Git
            self._log("[1/3] 检查 Git...")
            git_check = subprocess.run("git --version", shell=True, capture_output=True, text=True)
            if git_check.returncode != 0:
                self._log("❌ 未找到 Git")
                self._log("   请下载安装 Git：https://git-scm.com/download/win")
                self._log("   安装完成后重新点击【📦 安装】")
                return
            self._log(f"   {git_check.stdout.strip()} ✓")

            # 2. 检查 Node.js
            self._log("[2/3] 检查 Node.js...")
            node_check = subprocess.run("node --version", shell=True, capture_output=True, text=True)
            if node_check.returncode != 0:
                self._log("❌ 未找到 Node.js")
                self._log("   请下载安装 Node.js LTS：https://nodejs.org")
                self._log("   安装完成后重新点击【📦 安装】")
                return
            self._log(f"   Node.js {node_check.stdout.strip()} ✓")

            # 3. 安装 openclaw
            self._log("[3/3] 正在安装 openclaw（npm install -g openclaw）...")
            self._log("   这可能需要1-3分钟，请耐心等待...")
            result = subprocess.run(
                "npm install -g openclaw",
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                self._log(result.stdout)
            if result.returncode == 0:
                self._log("✅ openclaw 安装成功！点击【🚀 一键启动】即可运行。")
            else:
                self._log("❌ 安装失败：" + result.stderr)
        except Exception as e:
            self._log(f"安装出错：{e}")

    # ── 配置持久化 ────────────────────────────────────────────

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for name, cfg in data.get("models", {}).items():
                    if name in self.models_config:
                        self.models_config[name].update(cfg)
                if "model" in data:
                    self.model_var.set(data["model"])
                if "scene" in data:
                    self.scene_var.set(data["scene"])
                    self._on_scene_change(data["scene"])
                if "port" in data:
                    self.port_entry.delete(0, "end")
                    self.port_entry.insert(0, data["port"])
                if "concurrency" in data:
                    self.concurrency_entry.delete(0, "end")
                    self.concurrency_entry.insert(0, data["concurrency"])
                if "timeout" in data:
                    self.timeout_entry.delete(0, "end")
                    self.timeout_entry.insert(0, data["timeout"])
                self._on_model_change(self.model_var.get())
            except Exception:
                pass

    def _save_config(self):
        model_name = self.model_var.get()
        self.models_config[model_name]["api_key"] = self.api_key_entry.get().strip()
        self.models_config[model_name]["base_url"] = self.base_url_entry.get().strip()
        data = {
            "model": self.model_var.get(),
            "scene": self.scene_var.get(),
            "port": self.port_entry.get().strip(),
            "concurrency": self.concurrency_entry.get().strip(),
            "timeout": self.timeout_entry.get().strip(),
            "models": self.models_config,
        }
        os.makedirs(os.path.dirname(CONFIG_FILE) if os.path.dirname(CONFIG_FILE) else ".", exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self._log("配置已保存。")

    def _export_config(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json")],
            title="导出配置"
        )
        if path:
            model_name = self.model_var.get()
            self.models_config[model_name]["api_key"] = self.api_key_entry.get().strip()
            self.models_config[model_name]["base_url"] = self.base_url_entry.get().strip()
            data = {
                "model": self.model_var.get(),
                "scene": self.scene_var.get(),
                "port": self.port_entry.get().strip(),
                "concurrency": self.concurrency_entry.get().strip(),
                "timeout": self.timeout_entry.get().strip(),
                "models": self.models_config,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._log(f"配置已导出至：{path}")

    def _import_config(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON 文件", "*.json")],
            title="导入配置"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for name, cfg in data.get("models", {}).items():
                    if name in self.models_config:
                        self.models_config[name].update(cfg)
                if "model" in data:
                    self.model_var.set(data["model"])
                if "scene" in data:
                    self.scene_var.set(data["scene"])
                    self._on_scene_change(data["scene"])
                if "port" in data:
                    self.port_entry.delete(0, "end")
                    self.port_entry.insert(0, data["port"])
                if "concurrency" in data:
                    self.concurrency_entry.delete(0, "end")
                    self.concurrency_entry.insert(0, data["concurrency"])
                if "timeout" in data:
                    self.timeout_entry.delete(0, "end")
                    self.timeout_entry.insert(0, data["timeout"])
                self._on_model_change(self.model_var.get())
                self._log(f"配置已从 {path} 导入。")
            except Exception as e:
                messagebox.showerror("导入失败", str(e))

    # ── 聊天功能 ──────────────────────────────────────────────

    def _append_chat(self, text: str):
        def _do():
            self.chat_box.configure(state="normal")
            self.chat_box.insert("end", text + "\n")
            self.chat_box.see("end")
            self.chat_box.configure(state="disabled")
        self.after(0, _do)

    def _send_chat(self):
        msg = self.chat_input.get().strip()
        if not msg:
            return
        self.chat_input.delete(0, "end")
        self._append_chat(f"你：{msg}")
        threading.Thread(target=self._run_chat, args=(msg,), daemon=True).start()

    def _run_chat(self, msg: str):
        openclaw_cmd = shutil.which("openclaw")
        if not openclaw_cmd:
            candidates = [
                os.path.expanduser("~/.npm-global/bin/openclaw"),
                os.path.expanduser("~/AppData/Roaming/npm/openclaw.cmd"),
                r"C:\Users\Public\AppData\Roaming\npm\openclaw.cmd",
            ]
            for c in candidates:
                if os.path.isfile(c):
                    openclaw_cmd = c
                    break
        if not openclaw_cmd:
            self._append_chat("[错误] 未找到 openclaw，请先安装。")
            return
        try:
            result = subprocess.run(
                [openclaw_cmd, "agent", "--message", msg, "--json"],
                capture_output=True, text=True, timeout=60
            )
            output = result.stdout.strip()
            if output:
                try:
                    data = json.loads(output)
                    reply = data.get("reply") or data.get("message") or data.get("content") or output
                except Exception:
                    reply = output
            else:
                reply = result.stderr.strip() or "（无回复）"
            self._append_chat(f"OpenClaw：{reply}")
        except subprocess.TimeoutExpired:
            self._append_chat("[错误] 请求超时（60s）。")
        except Exception as e:
            self._append_chat(f"[错误] {e}")

    # ── 更新检查 ──────────────────────────────────────────────

    def _check_update_async(self):
        threading.Thread(target=self._check_update, daemon=True).start()

    def _check_update_manual(self):
        threading.Thread(target=self._check_update, args=(True,), daemon=True).start()

    def _check_update(self, manual=False):
        try:
            url = "https://raw.githubusercontent.com/changyunju/OnePersonClaw/main/version.json"
            with urllib.request.urlopen(url, timeout=5) as resp:
                info = json.loads(resp.read().decode())
            latest = info.get("version", VERSION)
            notes = info.get("notes", "")
            if latest != VERSION:
                self.update_btn.configure(
                    text=f"v{VERSION} → {latest}",
                    fg_color="#7a3a00", hover_color="#a05000"
                )
                if manual:
                    if messagebox.askyesno(
                        "发现新版本",
                        f"最新版本：{latest}\n\n更新说明：{notes}\n\n是否前往下载？"
                    ):
                        webbrowser.open("https://github.com/changyunju/OnePersonClaw/releases")
            else:
                self.update_btn.configure(text=f"v{VERSION} ✓", fg_color="#2a5a2a")
                if manual:
                    messagebox.showinfo("已是最新", f"当前版本 v{VERSION} 已是最新。")
        except Exception:
            if manual:
                messagebox.showwarning("检查失败", "无法连接更新服务器，请检查网络。")


if __name__ == "__main__":
    app = OnePersonClaw()
    app.mainloop()
