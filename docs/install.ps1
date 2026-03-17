# OnePersonClaw 一键安装脚本
# 使用方式: iwr -useb https://opc.yunjunet.cn/install.ps1 | iex

$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host '╔══════════════════════════════════════════════╗' -ForegroundColor Cyan
Write-Host '║      OnePersonClaw 一键安装程序              ║' -ForegroundColor Cyan
Write-Host '║      by 常云举19966519194                    ║' -ForegroundColor Cyan
Write-Host '╚══════════════════════════════════════════════╝' -ForegroundColor Cyan
Write-Host ''

function Install-Winget-Package {
    param([string]$PackageId, [string]$Name)
    Write-Host "   正在通过 winget 安装 $Name..." -ForegroundColor Gray
    try {
        winget install --id $PackageId --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
        Write-Host "   ✓ $Name 安装完成，请重启终端后重新运行本脚本" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 自动安装失败，请手动下载安装" -ForegroundColor Red
    }
}

# ── 1. 检查并安装 Git ────────────────────────────────────
Write-Host '[1/3] 检查 Git...' -ForegroundColor Yellow
$gitOk = $false
try {
    $gitVersion = & git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   $gitVersion ✓" -ForegroundColor Green
        $gitOk = $true
    }
} catch {}

if (-not $gitOk) {
    Write-Host '   未找到 Git，正在自动安装...' -ForegroundColor Yellow
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Install-Winget-Package 'Git.Git' 'Git'
        exit 0
    } else {
        Write-Host '   请手动下载安装 Git: https://git-scm.com/download/win' -ForegroundColor Red
        Start-Process 'https://git-scm.com/download/win'
        exit 1
    }
}

# ── 2. 检查并安装 Node.js ────────────────────────────────
Write-Host '[2/3] 检查 Node.js...' -ForegroundColor Yellow
$nodeOk = $false
try {
    $nodeVersion = & node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Node.js $nodeVersion ✓" -ForegroundColor Green
        $nodeOk = $true
    }
} catch {}

if (-not $nodeOk) {
    Write-Host '   未找到 Node.js，正在自动安装...' -ForegroundColor Yellow
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Install-Winget-Package 'OpenJS.NodeJS.LTS' 'Node.js LTS'
        exit 0
    } else {
        Write-Host '   请手动下载安装 Node.js LTS: https://nodejs.org' -ForegroundColor Red
        Start-Process 'https://nodejs.org'
        exit 1
    }
}

# ── 3. 安装 openclaw ────────────────────────────────────
Write-Host '[3/3] 正在安装 openclaw...' -ForegroundColor Yellow
Write-Host '   这可能需要 1-3 分钟，请耐心等待...' -ForegroundColor Gray

try {
    $output = & npm install -g openclaw 2>&1
    $output | ForEach-Object { Write-Host "   $_" }
    if ($LASTEXITCODE -ne 0) { throw "npm 返回错误码 $LASTEXITCODE" }
    Write-Host '   ✓ openclaw 安装成功' -ForegroundColor Green
} catch {
    Write-Host "   ❌ openclaw 安装失败: $_" -ForegroundColor Red
    exit 1
}

# ── 4. 配置免费共享 DeepSeek（火山引擎）───────────────────
Write-Host ''
Write-Host '正在配置免费共享 DeepSeek（火山引擎，限速 60次/分钟）...' -ForegroundColor Yellow

# 刷新 PATH 以找到刚安装的 openclaw
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')

$openclaw_cmd = (Get-Command openclaw -ErrorAction SilentlyContinue)?.Source
if (-not $openclaw_cmd) {
    foreach ($c in @("$env:APPDATA\npm\openclaw.cmd", "$env:APPDATA\npm\openclaw")) {
        if (Test-Path $c) { $openclaw_cmd = $c; break }
    }
}

if ($openclaw_cmd) {
    try {
        & $openclaw_cmd config set apiKey "18771050-2cfc-42b1-a212-4cf95de83aa7" 2>&1 | Out-Null
        & $openclaw_cmd config set baseUrl "https://ark.cn-beijing.volces.com/api/v3" 2>&1 | Out-Null
        & $openclaw_cmd config set model "deepseek-v3-2-251201" 2>&1 | Out-Null
        Write-Host '   ✓ 免费 DeepSeek 配置完成' -ForegroundColor Green
    } catch {
        Write-Host '   ⚠ 自动配置失败，在 OnePersonClaw 界面中留空 API Key 即可使用免费模型' -ForegroundColor Yellow
    }
} else {
    Write-Host '   ⚠ 请重启终端后运行 openclaw start' -ForegroundColor Yellow
}

# ── 完成 ────────────────────────────────────────────────
Write-Host ''
Write-Host '╔══════════════════════════════════════════════╗' -ForegroundColor Green
Write-Host '║   ✅  安装完成！                             ║' -ForegroundColor Green
Write-Host '║                                              ║' -ForegroundColor Green
Write-Host '║   运行: openclaw start                       ║' -ForegroundColor Green
Write-Host '║   下载 EXE: https://opc.yunjunet.cn          ║' -ForegroundColor Green
Write-Host '╚══════════════════════════════════════════════╝' -ForegroundColor Green
Write-Host ''
