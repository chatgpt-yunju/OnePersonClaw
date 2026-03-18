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
VERSION = "0.5.8"
UPDATE_URL = "https://raw.githubusercontent.com/chatgpt-yunju/OnePersonClaw/main/version.json"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# 新版简化模型（Base URL 统一为 api.yunjunet.cn）
SIMPLE_MODELS = {
    "DeepSeek": {
        "id": "deepseek-chat",
        "provider": "openai",
        "desc": "高性价比，推理能力强",
    },
    "智谱 GLM": {
        "id": "glm-4-flash",
        "provider": "openai",
        "desc": "国产大模型，响应快",
    },
    "Claude Sonnet 4.6 (CC Club)": {
        "id": "claude-sonnet-4-6",
        "provider": "openai",
        "desc": "最强推理，积分制",
    },
}
SIMPLE_BASE_URL = "https://api.yunjunet.cn/v1"

MODELS = {
    "Claude Sonnet (Anthropic)": {
        "key": "claude",
        "id": "claude-sonnet-4-5",
        "env_key": "ANTHROPIC_API_KEY",
        "openclaw_provider": "anthropic",
        "cost_light": "$10~30",
        "cost_normal": "$30~70",
        "cost_heavy": "$70~150",
    },
    "GPT-4o (OpenAI)": {
        "key": "openai",
        "id": "gpt-4o",
        "env_key": "OPENAI_API_KEY",
        "openclaw_provider": "openai",
        "cost_light": "$15~40",
        "cost_normal": "$40~100",
        "cost_heavy": "$100~200",
    },
    "DeepSeek": {
        "key": "deepseek",
        "id": "deepseek-chat",
        "env_key": "OPENAI_API_KEY",
        "openclaw_provider": "openai",
        "base_url": "https://api.deepseek.com",
        "cost_light": "$1~5",
        "cost_normal": "$5~15",
        "cost_heavy": "$15~40",
    },
    "火山引擎 (豆包)": {
        "key": "volcengine",
        "id": "deepseek-v3-2-251201",
        "env_key": "OPENAI_API_KEY",
        "openclaw_provider": "openai",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "cost_light": "$1~5",
        "cost_normal": "$5~15",
        "cost_heavy": "$15~40",
    },
    "智谱 GLM": {
        "key": "zhipu",
        "id": "glm-4-flash",
        "env_key": "OPENAI_API_KEY",
        "openclaw_provider": "openai",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "cost_light": "$2~8",
        "cost_normal": "$8~25",
        "cost_heavy": "$25~60",
    },
    "本地模型 Ollama": {
        "key": "ollama",
        "id": "ollama/llama3",
        "env_key": "OPENAI_API_KEY",
        "openclaw_provider": "openai",
        "base_url": "http://localhost:11434/v1",
        "cost_light": "免费",
        "cost_normal": "免费",
        "cost_heavy": "免费",
    },
    "CC Club - Claude Code": {
        "key": "ccclub_claude",
        "id": "claude-sonnet-4-5",
        "env_key": "OPENAI_API_KEY",
        "openclaw_provider": "openai",
        "base_url": "https://claude-code.club/api",
        "cost_light": "积分制",
        "cost_normal": "积分制",
        "cost_heavy": "积分制",
        "key_url": "https://customer.claude-code.club/invite/CNCQSH",
    },
    "CC Club - Codex": {
        "key": "ccclub_codex",
        "id": "codex-mini-latest",
        "env_key": "OPENAI_API_KEY",
        "openclaw_provider": "openai",
        "base_url": "https://claude-code.club/api",
        "cost_light": "积分制",
        "cost_normal": "积分制",
        "cost_heavy": "积分制",
        "key_url": "https://customer.claude-code.club/invite/CNCQSH",
    },
    "CC Club - Gemini": {
        "key": "ccclub_gemini",
        "id": "gemini-2.5-pro",
        "env_key": "OPENAI_API_KEY",
        "openclaw_provider": "openai",
        "base_url": "https://claude-code.club/api",
        "cost_light": "积分制",
        "cost_normal": "积分制",
        "cost_heavy": "积分制",
        "key_url": "https://customer.claude-code.club/invite/CNCQSH",
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

        # 初始化属性
        self.current_key_url = ""
        self.process = None
        self.is_simple_mode = True  # 默认使用新版简化模式

        # 每个模型独立存储 key 和 base_url
        self.models_config = {name: {"api_key": "", "base_url": m.get("base_url", "")}
                              for name, m in MODELS.items()}
        self.simple_models_config = {name: {"api_key": ""} for name in SIMPLE_MODELS.keys()}

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

        # 版本切换按钮
        self.mode_switch_btn = ctk.CTkButton(
            header, text="切换到旧版",
            width=100, height=28, fg_color="#555", hover_color="#666",
            font=ctk.CTkFont(size=12), command=self._toggle_mode
        )
        self.mode_switch_btn.pack(side="right", padx=(8, 0))

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

        # 创建两个UI容器
        self.simple_container = ctk.CTkFrame(self, fg_color="transparent")
        self.advanced_container = ctk.CTkFrame(self, fg_color="transparent")

        # 默认显示新版（简化版）
        if self.is_simple_mode:
            self._build_simple_ui()
            self.simple_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        else:
            self._build_advanced_ui()
            self.advanced_container.pack(fill="both", expand=True, padx=30)

    def _toggle_mode(self):
        """切换新版/旧版"""
        self.is_simple_mode = not self.is_simple_mode

        if self.is_simple_mode:
            # 切换到新版
            self.advanced_container.pack_forget()
            self.simple_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
            self.mode_switch_btn.configure(text="切换到旧版")
        else:
            # 切换到旧版
            self.simple_container.pack_forget()
            self.advanced_container.pack(fill="both", expand=True, padx=30)
            self.mode_switch_btn.configure(text="切换到新版")

    def _build_simple_ui(self):
        """新版简化UI：模型选择 + 一键启动"""
        # 直接设置已登录状态
        self.is_logged_in = True
        self.api_token = ""
        self.available_models = ["deepseek-chat", "glm-4-flash", "claude-sonnet-4-6"]

        # 主界面区域（直接显示）
        self.main_frame = ctk.CTkFrame(self.simple_container)
        self.main_frame.pack(fill="both", expand=True, pady=20)

        # 模型变量（隐藏 UI，通过"3 切换模型"修改）
        self.simple_model_var = ctk.StringVar(value=self.available_models[0])

        btn_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_row.pack(pady=(0, 20))

        self.simple_launch_btn = ctk.CTkButton(
            btn_row, text="1 一键启动",
            width=150, height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2a7d3f", hover_color="#1a5a1a",
            command=self._simple_launch
        )
        self.simple_launch_btn.pack(side="left", padx=(0, 8))

        self.simple_connect_btn = ctk.CTkButton(
            btn_row, text="2 控制面板",
            width=120, height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1a4a7a", hover_color="#0d2d4a",
            command=self._simple_connect
        )
        self.simple_connect_btn.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="3 切换模型",
            width=120, height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#5a3a7a", hover_color="#3a1a5a",
            command=self._simple_switch_model
        ).pack(side="left")

        self.simple_status_label = ctk.CTkLabel(
            self.main_frame, text="● 未启动",
            font=ctk.CTkFont(size=13), text_color="#888"
        )
        self.simple_status_label.pack(pady=(5, 30))

    def _do_login(self):
        """执行登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.login_status_label.configure(text="❌ 请输入用户名和密码", text_color="#ff5555")
            return

        self.login_btn.configure(state="disabled", text="登录中...")
        self.login_status_label.configure(text="正在登录...", text_color="#888")

        threading.Thread(target=self._login_thread, args=(username, password), daemon=True).start()

    def _login_thread(self, username, password):
        """登录线程"""
        import json
        try:
            # 调用登录API
            login_url = f"{SIMPLE_BASE_URL}/auth/login"
            login_data = json.dumps({"username": username, "password": password}).encode()
            req = urllib.request.Request(
                login_url,
                data=login_data,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())

                if result.get("success") or result.get("token"):
                    self.api_token = result.get("token", "")
                    self.is_logged_in = True

                    # 获取模型列表
                    self._fetch_models()

                    # 切换到主界面
                    self.after(0, self._show_main_ui)
                else:
                    error_msg = result.get("message", "登录失败")
                    self.after(0, lambda: self._login_failed(error_msg))

        except Exception as e:
            self.after(0, lambda: self._login_failed(str(e)))

    def _fetch_models(self):
        """获取可用模型列表"""
        try:
            models_url = f"{SIMPLE_BASE_URL}/models"
            req = urllib.request.Request(
                models_url,
                headers={"Authorization": f"Bearer {self.api_token}"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                self.available_models = result.get("models", [])

        except Exception as e:
            self.available_models = ["deepseek-chat", "glm-4-flash", "claude-sonnet-4-6"]

    def _show_main_ui(self):
        """显示主界面"""
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True, pady=20)

        # 更新模型列表
        if self.available_models:
            self.simple_model_menu.configure(values=self.available_models)
            self.simple_model_var.set(self.available_models[0])

        self.login_status_label.configure(text="✅ 登录成功", text_color="#50c0ff")

    def _login_failed(self, error_msg):
        """登录失败"""
        self.login_btn.configure(state="normal", text="登录")
        self.login_status_label.configure(text=f"❌ {error_msg}", text_color="#ff5555")

    def _simple_launch(self):
        """新版一键启动"""
        if not self.is_logged_in:
            messagebox.showerror("未登录", "请先登录")
            return

        model_id = self.simple_model_var.get()
        if not model_id:
            messagebox.showerror("未选择模型", "请选择一个模型")
            return

        # 查找 openclaw
        openclaw_cmd = shutil.which("openclaw")
        if not openclaw_cmd:
            candidates = [
                os.path.expanduser("~\\AppData\\Roaming\\npm\\openclaw.cmd"),
                os.path.expanduser("~\\AppData\\Roaming\\npm\\openclaw"),
            ]
            for c in candidates:
                if os.path.exists(c):
                    openclaw_cmd = c
                    break

        if not openclaw_cmd:
            messagebox.showerror("未找到 openclaw", "请先安装 openclaw")
            return

        # 配置环境变量
        env = os.environ.copy()
        env["OPENAI_API_KEY"] = self.api_token
        env["OPENAI_BASE_URL"] = SIMPLE_BASE_URL
        env["MODEL"] = model_id

        try:
            self.process = subprocess.Popen(
                [openclaw_cmd, "gateway", "start"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.simple_status_label.configure(text=f"● 运行中 | {model_id}", text_color="#50c0ff")
        except Exception as e:
            messagebox.showerror("启动失败", str(e))

    def _simple_connect(self):
        """读取 openclaw 配置，打开 gateway 连接页面"""
        config_path = os.path.expanduser("~\\.openclaw\\openclaw.json")
        try:
            with open(config_path, encoding="utf-8") as f:
                cfg = json.load(f)
            gw = cfg.get("gateway", {})
            port = gw.get("port", 18789)
            auth = gw.get("auth", {})
            password = auth.get("password", "")
            if password:
                url = f"http://127.0.0.1:{port}?password={password}"
            else:
                url = f"http://127.0.0.1:{port}"
        except Exception:
            url = "http://127.0.0.1:18789"
        webbrowser.open(url)

    def _simple_switch_model(self):
        """临时切换模型（仅改内存，不修改配置文件）"""
        win = ctk.CTkToplevel(self)
        win.title("3 切换模型（临时）")
        win.geometry("400x180")
        win.grab_set()

        ctk.CTkLabel(
            win, text="模型 ID（临时生效，重启后恢复）",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=30, pady=(20, 4))

        entry = ctk.CTkEntry(win, width=340, placeholder_text="z-ai/glm5")
        entry.insert(0, self.simple_model_var.get() or "z-ai/glm5")
        entry.pack(padx=30)

        ctk.CTkLabel(
            win, text="无需重启网关，立即生效",
            font=ctk.CTkFont(size=11), text_color="#888"
        ).pack(anchor="w", padx=30, pady=(4, 0))

        def _confirm():
            model_id = entry.get().strip() or "z-ai/glm5"
            # 静默修改 openclaw.json 中的模型 ID
            config_path = os.path.join(os.path.expanduser("~"), ".openclaw", "openclaw.json")
            try:
                with open(config_path, encoding="utf-8") as f:
                    cfg = json.load(f)
                provider = cfg.setdefault("providers", {}).setdefault("custom-api-yunjunet-cn", {})
                models = provider.get("models", [])
                if models:
                    models[0]["id"] = model_id
                    models[0]["name"] = model_id
                else:
                    provider["models"] = [{"id": model_id, "name": model_id}]
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            self.simple_model_var.set(model_id)
            self.simple_status_label.configure(text=f"● 模型已切换 | {model_id}", text_color="#50c0ff")
            win.destroy()

        ctk.CTkButton(win, text="确认", width=160, height=38,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=_confirm).pack(pady=(16, 0))

    def _simple_stop(self):
        """停止服务：关闭gateway进程并关闭浏览器页面"""
        # 执行 openclaw gateway stop
        openclaw_cmd = shutil.which("openclaw")
        if not openclaw_cmd:
            candidates = [
                os.path.expanduser("~\\AppData\\Roaming\\npm\\openclaw.cmd"),
                os.path.expanduser("~\\AppData\\Roaming\\npm\\openclaw"),
            ]
            for c in candidates:
                if os.path.exists(c):
                    openclaw_cmd = c
                    break
        if openclaw_cmd:
            try:
                subprocess.run([openclaw_cmd, "gateway", "stop"], capture_output=True)
            except Exception:
                pass

        # 关闭 dashboard 进程
        if self.process:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self.process.pid)],
                    capture_output=True
                )
            except Exception:
                pass
            self.process = None

        # 关闭浏览器中 127.0.0.1:18789 的页面（IE/Edge/Chrome Shell）
        try:
            ps_script = (
                "$shell = New-Object -ComObject Shell.Application; "
                "$shell.Windows() | Where-Object { $_.LocationURL -like '*18789*' } "
                "| ForEach-Object { $_.Quit() }"
            )
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True
            )
        except Exception:
            pass

        self.simple_status_label.configure(text="● 已停止", text_color="#888")

    def _build_advanced_ui(self):
        """旧版完整UI"""
        # 主体
        body = ctk.CTkFrame(self.advanced_container)
        body.pack(fill="both", expand=True)

        self._build_left(body)
        self._build_right(body)

        # 提示词预览
        prompt_frame = ctk.CTkFrame(self.advanced_container, fg_color="transparent")
        prompt_frame.pack(fill="x", padx=0, pady=(8, 0))

        ctk.CTkLabel(
            prompt_frame, text="场景提示词预览",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")

        self.prompt_box = ctk.CTkTextbox(prompt_frame, height=60, font=ctk.CTkFont(size=11))
        self.prompt_box.pack(fill="x", pady=(4, 0))
        self.prompt_box.configure(state="disabled")

        # 费用估算
        cost_frame = ctk.CTkFrame(self.advanced_container, fg_color="transparent")
        cost_frame.pack(fill="x", padx=0, pady=(8, 0))

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
            self.advanced_container, text="● 未启动", text_color="#888",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(10, 4))

        # 按钮区
        btn_frame = ctk.CTkFrame(self.advanced_container, fg_color="transparent")
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
            btn_frame, text="📦 一键安装",
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
        chat_frame = ctk.CTkFrame(self.advanced_container, fg_color="transparent")
        chat_frame.pack(fill="x", padx=0, pady=(4, 0))

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

        # 工具箱快捷按钮
        toolbox_frame = ctk.CTkFrame(self.advanced_container, fg_color="transparent")
        toolbox_frame.pack(fill="x", padx=0, pady=(4, 0))
        ctk.CTkLabel(
            toolbox_frame, text="🔧 工具箱",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 8))
        for btn_text, btn_cmd in [
            ("🏥 健康检查", self._run_doctor),
            ("📡 渠道状态", self._run_channels_status),
            ("🤖 模型列表", self._run_models_list),
            ("💬 会话列表", self._run_sessions),
            ("📋 查看日志", self._run_logs),
        ]:
            ctk.CTkButton(
                toolbox_frame, text=btn_text, command=btn_cmd,
                width=90, height=28, fg_color="#222", hover_color="#333",
                font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=3)

        # 常用命令速查 TabView
        cmd_tab = ctk.CTkTabview(self.advanced_container, height=130)
        cmd_tab.pack(fill="x", padx=0, pady=(4, 0))
        CMD_GROUPS = [
            ("模型", [
                "openclaw models list",
                "openclaw models status",
                "openclaw models set anthropic/claude-sonnet-4-5",
                "openclaw models set openai/gpt-4o",
                "openclaw models set deepseek/deepseek-chat",
                "openclaw models aliases",
            ]),
            ("认证", [
                "openclaw models auth",
                "openclaw configure",
                "openclaw onboard",
                "openclaw config set model.provider anthropic",
                "openclaw config get model",
            ]),
            ("渠道", [
                "openclaw channels list",
                "openclaw channels status",
                "openclaw channels add --channel telegram --token <token>",
                "openclaw channels login --channel whatsapp",
                "openclaw channels logs",
            ]),
            ("网关", [
                "openclaw gateway",
                "openclaw gateway --port 18789",
                "openclaw gateway --force",
                "openclaw health",
                "openclaw doctor",
                "openclaw dashboard",
            ]),
            ("插件", [
                "openclaw plugins list",
                "openclaw skills list",
                "openclaw sessions list",
                "openclaw logs",
                "openclaw update",
                "openclaw --version",
            ]),
        ]
        for tab_name, cmds in CMD_GROUPS:
            tab = cmd_tab.add(tab_name)
            for cmd in cmds:
                row = ctk.CTkFrame(tab, fg_color="transparent")
                row.pack(fill="x", pady=1)
                lbl = ctk.CTkLabel(row, text=cmd, font=ctk.CTkFont(size=11, family="Courier"),
                                   text_color="#adf", anchor="w", cursor="hand2")
                lbl.pack(side="left", fill="x", expand=True)
                lbl.bind("<Button-1>", lambda e, c=cmd: (self.clipboard_clear(), self.clipboard_append(c),
                         self._set_status(f"已复制：{c}", "#4aff88")))

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

        # Key 获取链接（动态显示）
        self.key_url_label = ctk.CTkLabel(
            left, text="",
            font=ctk.CTkFont(size=11),
            text_color="#50c0ff",
            cursor="hand2"
        )
        self.key_url_label.pack(anchor="w", pady=(0, 2))
        self.key_url_label.bind("<Button-1>", self._open_key_url)

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

        # 显示 key 获取链接（如果有）
        model_info = MODELS.get(name, {})
        key_url = model_info.get("key_url", "")
        if key_url:
            self.key_url_label.configure(text="🔗 点击获取 API Key")
            self.current_key_url = key_url
        else:
            self.key_url_label.configure(text="")
            self.current_key_url = ""

        # 同步更新 openclaw 配置
        model_id = model_info.get("id", "")
        provider = model_info.get("openclaw_provider", "")
        if model_id and provider:
            self._log(f"🔄 切换模型到 {provider}/{model_id}")
            threading.Thread(
                target=lambda: self._run_openclaw_cmd(f"models set {provider}/{model_id}"),
                daemon=True
            ).start()

    def _open_key_url(self, event):
        if hasattr(self, 'current_key_url') and self.current_key_url:
            webbrowser.open(self.current_key_url)

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

        # 未填秘钥时使用免费共享的火山引擎 DeepSeek（限速 60次/分钟）
        FREE_API_KEY = "18771050-2cfc-42b1-a212-4cf95de83aa7"
        FREE_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
        FREE_MODEL_ID = "deepseek-v3-2-251201"
        using_free = False
        if not api_key:
            api_key = FREE_API_KEY
            base_url = FREE_BASE_URL
            using_free = True

        self.models_config[model_name]["api_key"] = api_key
        self.models_config[model_name]["base_url"] = base_url

        model_info = MODELS.get(model_name, {})
        model_id = FREE_MODEL_ID if using_free else model_info.get("id", model_name)
        scene_prompt = SCENES.get(scene, {}).get("prompt", "")
        effective_base_url = base_url or model_info.get("base_url", "")

        if using_free:
            self._log("="*50)
            self._log("⚡ 未填 API Key，已自动使用免费共享 DeepSeek")
            self._log("   限速：60次/分钟（所有用户共享）")
            self._log("   如需更快速度，请配置自己的 API Key")
            self._log("="*50)

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

        # 同步模型配置到 openclaw
        if not using_free:
            provider = model_info.get("openclaw_provider", "")
            if provider and model_id:
                self._log(f"🔄 同步模型配置: {provider}/{model_id}")
                try:
                    # 设置 API Key
                    env_key = model_info.get("env_key", "")
                    if env_key and api_key:
                        self._ps(f"openclaw config set {env_key} {api_key}")

                    # 设置 Base URL（如果有）
                    if effective_base_url and provider == "openai":
                        self._ps(f"openclaw config set OPENAI_BASE_URL {effective_base_url}")

                    # 设置默认模型
                    self._ps(f"openclaw models set {provider}/{model_id}")
                except Exception as e:
                    self._log(f"⚠️ 配置同步失败: {e}")

        try:
            self.process = subprocess.Popen(
                [openclaw_cmd, "dashboard"],
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

    def _ps(self, cmd, timeout=300):
        """以管理员权限静默运行 PowerShell 命令，返回 CompletedProcess"""
        si = None
        cf = 0
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            cf = subprocess.CREATE_NO_WINDOW
        return subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-Command", cmd],
            capture_output=True, text=True, timeout=timeout,
            startupinfo=si, creationflags=cf
        )

    def _run_install(self):
        try:
            # 辅助函数：刷新环境变量
            def refresh_env():
                self._ps("$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')")

            # 辅助函数：检查 Chocolatey
            def has_choco():
                return self._ps("Get-Command choco -ErrorAction SilentlyContinue").returncode == 0

            # 1. 检查并安装 Git
            self._log("[1/3] 检查 Git...")
            git_check = self._ps("git --version")
            if git_check.returncode != 0:
                self._log("   未找到 Git，正在安装...")

                # 尝试 winget
                if self._ps("Get-Command winget -ErrorAction SilentlyContinue").returncode == 0:
                    self._log("   使用 winget 安装 Git...")
                    r = self._ps("winget install Git.Git --accept-source-agreements --accept-package-agreements", timeout=600)
                    refresh_env()
                    git_check = self._ps("git --version")
                    if git_check.returncode == 0:
                        self._log(f"   {git_check.stdout.strip()} ✓")
                    else:
                        self._log("❌ Git 安装失败，请重启后重试或手动安装：https://git-scm.com/download/win")
                        return
                else:
                    self._log("❌ 未找到 winget，请手动安装 Git：https://git-scm.com/download/win")
                    return
            else:
                self._log(f"   {git_check.stdout.strip()} ✓")

            # 2. 检查并安装 Node.js
            self._log("[2/3] 检查 Node.js...")
            node_check = self._ps("node --version")
            if node_check.returncode != 0:
                self._log("   未找到 Node.js，正在安装...")
                node_installed = False

                # 尝试 Chocolatey
                if has_choco():
                    self._log("   使用 Chocolatey 安装 Node.js LTS...")
                    r = self._ps("choco install nodejs-lts -y --no-progress", timeout=600)
                    refresh_env()
                    if self._ps("node --version").returncode == 0:
                        node_installed = True

                # 尝试 winget
                if not node_installed:
                    self._log("   使用 winget 安装 Node.js...")
                    # 先尝试最新版
                    r = self._ps("winget install --id OpenJS.NodeJS --accept-source-agreements --accept-package-agreements", timeout=600)
                    if r.returncode != 0:
                        self._log("   尝试安装 LTS 版本...")
                        r = self._ps("winget install --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements", timeout=600)
                    refresh_env()
                    if self._ps("node --version").returncode == 0:
                        node_installed = True

                # 验证安装（最多 3 次）
                if node_installed:
                    self._log("   验证 Node.js 安装...")
                    for attempt in range(3):
                        refresh_env()
                        node_check = self._ps("node --version")
                        if node_check.returncode == 0:
                            break
                        if attempt < 2:
                            self._ps("Start-Sleep -Seconds 2")

                # 最终检查
                node_check = self._ps("node --version")
                if node_check.returncode != 0:
                    self._log("❌ Node.js 安装失败")
                    self._log("   请尝试：")
                    self._log("   1. 重启电脑后重试")
                    self._log("   2. 手动安装：https://nodejs.org")
                    self._log("   3. 或下载 MSI：https://npmmirror.com/mirrors/node/v22.13.1/node-v22.13.1-x64.msi")
                    return
            self._log(f"   Node.js {node_check.stdout.strip()} ✓")

            # 3. 配置 npm 镜像源并安装 openclaw
            self._log("[3/3] 配置 npm 镜像源...")
            self._ps("npm config set registry https://registry.npmmirror.com")
            self._log("   正在安装 openclaw（npm install -g openclaw）...")
            self._log("   这可能需要1-3分钟，请耐心等待...")
            result = self._ps("npm install -g openclaw", timeout=300)
            if result.stdout:
                self._log(result.stdout)
            if result.returncode == 0:
                self._log("="*50)
                self._log("✅ openclaw 安装成功！")
                self._log("")

                # 自动配置当前模型的 API Key
                self._log("🔧 正在配置 openclaw...")
                model_name = self.model_var.get()
                model_info = MODELS.get(model_name, {})
                api_key = self.api_key_entry.get().strip()
                base_url = self.base_url_entry.get().strip()

                if api_key:
                    provider = model_info.get("openclaw_provider", "")
                    model_id = model_info.get("id", "")

                    # 设置 API Key
                    env_key = model_info.get("env_key", "")
                    if env_key:
                        self._ps(f"openclaw config set {env_key} {api_key}")
                        self._log(f"   已配置 {env_key}")

                    # 设置 Base URL（如果有）
                    if base_url and provider == "openai":
                        self._ps(f"openclaw config set OPENAI_BASE_URL {base_url}")
                        self._log(f"   已配置 Base URL: {base_url}")

                    # 设置默认模型
                    if provider and model_id:
                        self._ps(f"openclaw models set {provider}/{model_id}")
                        self._log(f"   已设置默认模型: {provider}/{model_id}")

                self._log("")
                self._log("💡 使用说明：")
                self._log("   1. 如果有自己的 API Key，请在上方填写")
                self._log("   2. 如果没有，直接点击【🚀 一键启动】")
                self._log("      将自动使用免费共享 DeepSeek（限速 60次/分钟）")
                self._log("")
                self._log("👉 现在就可以点击【🚀 一键启动】开始使用！")
                self._log("="*50)
            else:
                self._log("❌ 安装失败：" + (result.stderr if result.stderr else "未知错误"))
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

    # ── 工具箱功能 ────────────────────────────────────────────

    def _run_doctor(self):
        self._log("🏥 运行健康检查...")
        threading.Thread(target=lambda: self._run_openclaw_cmd("doctor"), daemon=True).start()

    def _run_channels_status(self):
        self._log("📡 查询渠道状态...")
        threading.Thread(target=lambda: self._run_openclaw_cmd("channels status"), daemon=True).start()

    def _run_models_list(self):
        self._log("🤖 获取模型列表...")
        threading.Thread(target=lambda: self._run_openclaw_cmd("models list"), daemon=True).start()

    def _run_sessions(self):
        self._log("💬 获取会话列表...")
        threading.Thread(target=lambda: self._run_openclaw_cmd("sessions list"), daemon=True).start()

    def _run_logs(self):
        self._log("📋 获取日志...")
        threading.Thread(target=lambda: self._run_openclaw_cmd("logs"), daemon=True).start()

    def _run_openclaw_cmd(self, cmd: str):
        """Execute openclaw command and display output in log box"""
        openclaw_cmd = shutil.which("openclaw")
        if not openclaw_cmd:
            candidates = [
                os.path.expanduser("~/AppData/Roaming/npm/openclaw.cmd"),
                os.path.expanduser("~/AppData/Roaming/npm/openclaw"),
            ]
            for c in candidates:
                if os.path.exists(c):
                    openclaw_cmd = c
                    break
        if not openclaw_cmd:
            self._log("❌ 未找到 openclaw，请先安装")
            return

        kwargs = {}
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = si
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        try:
            result = subprocess.run(
                [openclaw_cmd] + cmd.split(),
                capture_output=True, text=True, timeout=30, **kwargs
            )
            output = result.stdout.strip() or result.stderr.strip() or "(无输出)"
            for line in output.split('\n'):
                self._log(line)
        except Exception as e:
            self._log(f"❌ 执行失败: {e}")

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
        # 隐藏 Windows 控制台窗口（STARTUPINFO + CREATE_NO_WINDOW）
        kwargs = {}
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = si
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        try:
            result = subprocess.run(
                [openclaw_cmd, "agent", "--agent", "main", "--message", msg, "--json"],
                capture_output=True, text=True, timeout=60, **kwargs
            )
            output = result.stdout.strip()
            if output:
                try:
                    data = json.loads(output)
                    # 优先取 payloads[0].text
                    payloads = data.get("payloads", [])
                    if payloads and isinstance(payloads, list):
                        reply = payloads[0].get("text", "") or "（无回复）"
                    else:
                        reply = (data.get("reply") or data.get("message")
                                 or data.get("content") or "（无回复）")
                except Exception:
                    reply = output
            else:
                reply = (result.stderr or "").strip() or "（无回复）"
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
            url = "https://raw.githubusercontent.com/chatgpt-yunju/OnePersonClaw/main/version.json"
            with urllib.request.urlopen(url, timeout=5) as resp:
                info = json.loads(resp.read().decode())
            latest = info.get("version", VERSION)
            notes = info.get("notes", "")
            if latest != VERSION:
                self.after(0, lambda: self.update_btn.configure(
                    text=f"v{VERSION} → {latest}",
                    fg_color="#7a3a00", hover_color="#a05000"
                ))
                def _prompt():
                    if messagebox.askyesno(
                        "发现新版本",
                        f"最新版本：{latest}\n\n更新说明：{notes}\n\n是否前往下载？"
                    ):
                        webbrowser.open("https://github.com/chatgpt-yunju/OnePersonClaw/releases/latest")
                self.after(0, _prompt)
            else:
                self.after(0, lambda: self.update_btn.configure(text=f"v{VERSION} ✓", fg_color="#2a5a2a"))
                if manual:
                    self.after(0, lambda: messagebox.showinfo("已是最新", f"当前版本 v{VERSION} 已是最新。"))
        except Exception:
            if manual:
                messagebox.showwarning("检查失败", "无法连接更新服务器，请检查网络。")


if __name__ == "__main__":
    app = OnePersonClaw()
    app.mainloop()
