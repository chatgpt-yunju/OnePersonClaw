# OnePersonClaw 一键安装脚本
# 自动安装 Git、Node.js 和 openclaw
# 作者: 常云举19966519194

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "需要管理员权限，正在重新启动..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OnePersonClaw 一键安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查并安装 Chocolatey（Windows 包管理器）
Write-Host "[0/4] 检查 Chocolatey 包管理器..." -ForegroundColor Green
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
if (-not $chocoInstalled) {
    Write-Host "   未找到 Chocolatey，正在安装..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Host "   Chocolatey 安装完成 ✓" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ Chocolatey 安装失败: $_" -ForegroundColor Red
        Write-Host "   将使用直接下载方式安装..." -ForegroundColor Yellow
    }
} else {
    Write-Host "   Chocolatey 已安装 ✓" -ForegroundColor Gray
}

# 2. 检查并安装 Git
Write-Host ""
Write-Host "[1/4] 检查 Git..." -ForegroundColor Green
try {
    $gitVersion = git --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   $gitVersion ✓" -ForegroundColor Gray
    } else {
        throw "Git not found"
    }
} catch {
    Write-Host "   未找到 Git，正在安装..." -ForegroundColor Yellow
    $chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoInstalled) {
        Write-Host "   使用 Chocolatey 安装 Git..." -ForegroundColor Gray
        choco install git -y --no-progress
    } else {
        Write-Host "   使用 winget 安装 Git..." -ForegroundColor Gray
        winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
    }

    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    $gitVersion = git --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   $gitVersion ✓" -ForegroundColor Gray
    } else {
        Write-Host "   ❌ Git 安装失败，请重启后重试或手动安装: https://git-scm.com/download/win" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

# 3. 检查并安装 Node.js
Write-Host ""
Write-Host "[2/4] 检查 Node.js..." -ForegroundColor Green
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Node.js $nodeVersion ✓" -ForegroundColor Gray
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Host "   未找到 Node.js，正在安装..." -ForegroundColor Yellow
    $chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoInstalled) {
        Write-Host "   使用 Chocolatey 安装 Node.js..." -ForegroundColor Gray
        choco install nodejs-lts -y --no-progress
    } else {
        Write-Host "   使用 winget 安装 Node.js..." -ForegroundColor Gray
        winget install --id OpenJS.NodeJS.LTS -e --source winget --silent --accept-package-agreements --accept-source-agreements
    }

    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Node.js $nodeVersion ✓" -ForegroundColor Gray
    } else {
        Write-Host "   ❌ Node.js 安装失败，请重启后重试或手动安装: https://nodejs.org" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

# 4. 配置 npm 镜像源并升级
Write-Host ""
Write-Host "[3/4] 配置 npm 镜像源并升级..." -ForegroundColor Green
try {
    Write-Host "   配置淘宝镜像源..." -ForegroundColor Gray
    npm config set registry https://registry.npmmirror.com 2>&1 | Out-Null
    Write-Host "   正在升级 npm 到最新版..." -ForegroundColor Gray
    npm install -g npm@latest 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $npmVersion = npm --version 2>$null
        Write-Host "   npm $npmVersion ✓" -ForegroundColor Gray
    } else {
        Write-Host "   npm 升级跳过（已是最新版）" -ForegroundColor Gray
    }
} catch {
    Write-Host "   npm 升级跳过: $_" -ForegroundColor Gray
}

# 5. 安装 openclaw
Write-Host ""
Write-Host "[4/4] 安装 openclaw..." -ForegroundColor Green
Write-Host "   正在执行: npm install -g openclaw" -ForegroundColor Gray
Write-Host "   这可能需要1-3分钟，请耐心等待..." -ForegroundColor Yellow
try {
    $installOutput = npm install -g openclaw 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ✅ 安装完成！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "已安装组件:" -ForegroundColor Cyan
        Write-Host "  • Git: $(git --version)" -ForegroundColor Gray
        Write-Host "  • Node.js: $(node --version)" -ForegroundColor Gray
        Write-Host "  • npm: $(npm --version)" -ForegroundColor Gray
        Write-Host "  • openclaw: $(openclaw --version)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "下一步:" -ForegroundColor Cyan
        Write-Host "  1. 运行 OnePersonClaw.exe" -ForegroundColor Gray
        Write-Host "  2. 点击【🚀 一键启动】按钮" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ openclaw 安装失败" -ForegroundColor Red
        Write-Host "错误信息:" -ForegroundColor Yellow
        Write-Host $installOutput -ForegroundColor Gray
        Write-Host ""
        Write-Host "请尝试:" -ForegroundColor Yellow
        Write-Host "  1. 重启电脑后重新运行此脚本" -ForegroundColor Gray
        Write-Host "  2. 手动执行: npm install -g openclaw" -ForegroundColor Gray
        Write-Host "  3. 访问 https://github.com/chatgpt-yunju/OnePersonClaw 获取帮助" -ForegroundColor Gray
    }
} catch {
    Write-Host ""
    Write-Host "❌ 安装出错: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "按回车键退出"
