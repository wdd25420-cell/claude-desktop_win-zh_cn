# Claude Desktop 中文汉化 - 安装脚本
param(
  [string]$AppDir
)

$ErrorActionPreference = 'Stop'

# Admin check
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
  [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
  Write-Host '需要管理员权限，请右键 -> 以管理员身份运行 PowerShell。' -ForegroundColor Red
  Read-Host '按 Enter 退出'
  exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) {
  Write-Host '未找到 Python 3，请先安装 Python 3。' -ForegroundColor Red
  exit 1
}

Get-Process -Name claude -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host 'WindowsApps zh-CN 补丁 (JSON + JS 界面文本 + 字体自定义器)'
Write-Host ''

Write-Host '步骤 1: JSON 资源...'
if ($AppDir) {
  & $python.Source "$scriptDir\patch_windowsapps_json_only.py" --app-dir "$AppDir"
} else {
  & $python.Source "$scriptDir\patch_windowsapps_json_only.py"
}

if ($LASTEXITCODE -ne 0) {
  Write-Host ''
  Write-Host 'JSON 补丁失败，请检查上方错误。' -ForegroundColor Red
  Read-Host '按 Enter 退出'
  exit 1
}

Write-Host ''
Write-Host '步骤 2: JS 界面文本和字体自定义器...'
if ($AppDir) {
  & $python.Source "$scriptDir\patch_chunks_zh_cn.py" --app-dir "$AppDir"
} else {
  & $python.Source "$scriptDir\patch_chunks_zh_cn.py"
}

Write-Host ''
Write-Host '补丁完成。重新打开 Claude Desktop 即可看到中文界面。' -ForegroundColor Green
Write-Host '中文字体设置可在设置 -> 外观中找到。' -ForegroundColor Green

Read-Host '按 Enter 退出'
