#!/bin/bash
# OnePersonClaw 打包脚本
source venv/bin/activate
pyinstaller --onefile --windowed \
  --name "OnePersonClaw" \
  --add-data "config.json:." \
  main.py
echo "打包完成：dist/OnePersonClaw"
