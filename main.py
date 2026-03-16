import customtkinter as ctk
import subprocess
import json
import os
import threading
import urllib.request

# ── 常量 ─────────────────────────────────────────────────────
VERSION = "1.2.0"
UPDATE_URL = "https://raw.githubusercontent.com/OnePersonClaw/releases/main/version.json"
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
        "prompt": "你是一个全能AI助手，帮助用户完成各类任务。",
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
            "- 用OpenClaw搭建个人自动化系统\n\n"
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
        self.geometry("760x620")
        self.resizable(False, False)
        self.process = None
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
            header, text="by 常云举",
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
        btn_frame.pack(pady=(0, 18))

        self.launch_btn = ctk.CTkButton(
            btn_frame, text="🚀 一键启动",
            command=self._launch, width=180, height=44,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.launch_btn.pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame, text="⏹ 停止",
            command=self._stop, width=100, height=44,
            fg_color="#555", hover_color="#333",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame, text="💾 保存",
            command=self._save_config, width=100, height=44,
            fg_color="#2a7a2a", hover_color="#1a5a1a",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=8)

    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)

        # 模型
        ctk.CTkLabel(left, text="选择模型", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.model_var = ctk.StringVar(value=list(MODELS.keys())[0])
        ctk.CTkOptionMenu(
            left, values=list(MODELS.keys()),
            variable=self.model_var, width=280,
            command=self._on_model_change
        ).pack(anchor="w", pady=(4, 14))

        # API Key
        ctk.CTkLabel(left, text="API Key", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.api_key_entry = ctk.CTkEntry(
            left, width=280, show="●", placeholder_text="输入你的 API Key"
        )
        self.api_key_entry.pack(anchor="w", pady=(4, 4))

        self.show_key_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            left, text="显示 Key", variable=self.show_key_var,
            command=self._toggle_key, font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(0, 14))

        # Base URL
        ctk.CTkLabel(left, text="Base URL（可选）", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.base_url_entry = ctk.CTkEntry(
            left, width=280, placeholder_text="默认官方接口"
        )
        self.base_url_entry.pack(anchor="w", pady=(4, 0))

    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.pack(side="right", fill="both", padx=(8, 16), pady=16)

        ctk.CTkLabel(right, text="场景模板", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        self.scene_var = ctk.StringVar(value=list(SCENES.keys())[0])
        for name, info in SCENES.items():
            row = ctk.CTkFrame(right, fg_color="transparent")
            row.pack(anchor="w", pady=2)
            ctk.CTkRadioButton(
                row, text=name, value=name, variable=self.scene_var,
                command=self._on_scene_change, font=ctk.CTkFont(size=12)
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=f"  {info['desc']}",
                font=ctk.CTkFont(size=10), text_color="#666"
            ).pack(side="left")

    # ── 事件处理 ──────────────────────────────────────────────

    def _toggle_key(self):
        self.api_key_entry.configure(show="" if self.show_key_var.get() else "●")

    def _set_status(self, text, color="#888"):
        self.status_label.configure(text=text, text_color=color)

    def _on_model_change(self, _=None):
        self._update_cost()
        model_info = MODELS[self.model_var.get()]
        default_url = model_info.get("base_url", "")
        self.base_url_entry.delete(0, "end")
        if default_url:
            self.base_url_entry.insert(0, default_url)

    def _on_scene_change(self):
        scene = self.scene_var.get()
        prompt = SCENES[scene]["prompt"]
        self.prompt_box.configure(state="normal")
        self.prompt_box.delete("1.0", "end")
        self.prompt_box.insert("1.0", prompt)
        self.prompt_box.configure(state="disabled")

    def _update_cost(self, _=None):
        model_info = MODELS[self.model_var.get()]
        level = self.usage_var.get()
        cost_map = {
            "轻度使用": model_info["cost_light"],
            "正常使用": model_info["cost_normal"],
            "重度使用": model_info["cost_heavy"],
        }
        self.cost_label.configure(text=f"≈ {cost_map[level]} / 月")

    # ── 启动/停止 ─────────────────────────────────────────────

    def _launch(self):
        api_key = self.api_key_entry.get().strip()
        model_name = self.model_var.get()
        model_info = MODELS[model_name]
        scene = self.scene_var.get()

        if model_info["key"] != "ollama" and not api_key:
            self._set_status("⚠ 请输入 API Key", "#e05050")
            return

        self._save_config()
        self._set_status(f"● 启动中 [{model_name} | {scene}]...", "#f0a020")
        self.launch_btn.configure(state="disabled")

        env = os.environ.copy()
        env[model_info["env_key"]] = api_key or "ollama"

        base_url = self.base_url_entry.get().strip() or model_info.get("base_url", "")
        if base_url:
            env["OPENAI_BASE_URL"] = base_url

        # 写入场景提示词供 OpenClaw 读取
        env["ONEPERSONCLAW_SCENE"] = scene
        env["ONEPERSONCLAW_PROMPT"] = SCENES[scene]["prompt"]

        def run():
            try:
                self.process = subprocess.Popen(["openclaw"], env=env)
                self.after(0, lambda: self._set_status(
                    f"✅ 运行中 [{model_name} | {scene}]", "#50c050"
                ))
            except FileNotFoundError:
                self.after(0, lambda: self._set_status(
                    "⚠ 未找到 openclaw，请先安装", "#e05050"
                ))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"⚠ 错误：{e}", "#e05050"))
            finally:
                self.after(0, lambda: self.launch_btn.configure(state="normal"))

        threading.Thread(target=run, daemon=True).start()

    def _stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process = None
            self._set_status("⏹ 已停止", "#888")
        else:
            self._set_status("● 未在运行", "#888")

    # ── 配置存读 ──────────────────────────────────────────────

    def _save_config(self):
        config = {
            "model": self.model_var.get(),
            "api_key": self.api_key_entry.get().strip(),
            "base_url": self.base_url_entry.get().strip(),
            "scene": self.scene_var.get(),
            "usage": self.usage_var.get(),
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self._set_status("✅ 配置已保存", "#50c050")

    def _load_config(self):
        if not os.path.exists(CONFIG_FILE):
            self._on_scene_change()
            self._update_cost()
            return
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cfg = json.load(f)
            if cfg.get("model") in MODELS:
                self.model_var.set(cfg["model"])
            if cfg.get("api_key"):
                self.api_key_entry.insert(0, cfg["api_key"])
            if cfg.get("base_url"):
                self.base_url_entry.insert(0, cfg["base_url"])
            if cfg.get("scene") in SCENES:
                self.scene_var.set(cfg["scene"])
            if cfg.get("usage") in USAGE_LEVELS:
                self.usage_var.set(cfg["usage"])
        except Exception:
            pass
        self._on_scene_change()
        self._update_cost()

    # ── 自动更新 ──────────────────────────────────────────────

    def _check_update_async(self):
        threading.Thread(target=self._fetch_update, daemon=True).start()

    def _check_update_manual(self):
        self.update_btn.configure(text="检查中...", state="disabled")
        threading.Thread(target=self._fetch_update, args=(True,), daemon=True).start()

    def _fetch_update(self, manual=False):
        try:
            req = urllib.request.urlopen(UPDATE_URL, timeout=5)
            data = json.loads(req.read().decode())
            latest = data.get("version", VERSION)
            notes = data.get("notes", "")
            download_url = data.get("download_url", "")

            if latest != VERSION:
                self.after(0, lambda: self._show_update(latest, notes, download_url))
            elif manual:
                self.after(0, lambda: self._set_status("✅ 已是最新版本", "#50c050"))
                self.after(0, lambda: self.update_btn.configure(
                    text=f"v{VERSION} ✅", state="normal"
                ))
        except Exception:
            if manual:
                self.after(0, lambda: self._set_status("⚠ 检查更新失败，请检查网络", "#e05050"))
                self.after(0, lambda: self.update_btn.configure(
                    text=f"v{VERSION}", state="normal"
                ))

    def _show_update(self, latest, notes, download_url):
        self.update_btn.configure(
            text=f"🆕 v{latest} 可更新",
            fg_color="#c07000", hover_color="#a05000",
            state="normal",
            command=lambda: self._do_update(download_url)
        )
        self._set_status(f"🆕 发现新版本 v{latest}：{notes}", "#f0a020")

    def _do_update(self, download_url):
        if not download_url:
            self._set_status("⚠ 暂无下载链接，请前往 GitHub 手动更新", "#e05050")
            return

        self._set_status("⬇ 下载更新中...", "#f0a020")

        def download():
            try:
                save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OnePersonClaw_new.exe")
                urllib.request.urlretrieve(download_url, save_path)
                self.after(0, lambda: self._set_status(
                    f"✅ 下载完成：{save_path}，请手动替换并重启", "#50c050"
                ))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"⚠ 下载失败：{e}", "#e05050"))

        threading.Thread(target=download, daemon=True).start()


if __name__ == "__main__":
    app = OnePersonClaw()
    app.mainloop()
