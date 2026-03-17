# OnePersonClaw 一键安装脚本
# 自动安装 Git、Node.js 和 openclaw

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "需要管理员权限，正在重新启动..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OnePersonClaw 一键安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查并安装 Git
Write-Host "[1/3] 检查 Git..." -ForegroundColor Green
$gitVersion = git --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   使用 winget 安装 Git..." -ForegroundColor Yellow
    winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "   完成 ✓" -ForegroundColor Gray
} else {
    Write-Host "   $gitVersion ✓" -ForegroundColor Gray
}

# 检查并安装 Node.js
Write-Host "[2/3] 检查 Node.js..." -ForegroundColor Green
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   使用 winget 安装 Node.js..." -ForegroundColor Yellow
    winget install --id OpenJS.NodeJS.LTS -e --source winget --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "   完成 ✓" -ForegroundColor Gray
} else {
    Write-Host "   Node.js $nodeVersion ✓" -ForegroundColor Gray
}

# 配置 npm 镜像源并安装 openclaw
Write-Host "[3/3] 安装 openclaw（1-3分钟）..." -ForegroundColor Green
npm config set registry https://registry.npmmirror.com 2>&1 | Out-Null
npm install -g openclaw
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ 安装完成！" -ForegroundColor Green
    Write-Host "   运行 OnePersonClaw.exe 开始使用" -ForegroundColor Gray
} else {
    Write-Host "❌ 安装失败，请重启后重试" -ForegroundColor Red
}

Write-Host ""
Read-Host "按回车键退出"
