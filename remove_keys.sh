#!/bin/bash

echo "开始删除所有历史中的 sk- API keys..."

git filter-branch --force --tree-filter '
  find . -type f ! -path "./.git/*" -exec sed -i "s/sk-[A-Za-z0-9]\{10,\}/\"\"/g" {} +
' --tag-name-filter cat -- --all

echo "清理旧对象..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "完成 请确认删除成功。"