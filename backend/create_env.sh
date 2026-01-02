#!/bin/bash

echo "正在创建 .env 配置文件..."

if [ -f .env ]; then
    read -p ".env 文件已存在，是否覆盖？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi
fi

cp env.example .env
echo ".env 文件已创建！"
echo ""
echo "请编辑 .env 文件，配置以下信息："
echo "1. DB_PASSWORD - MySQL数据库密码"
echo "2. DASHSCOPE_API_KEY - 通义千问API密钥"
echo "3. SECRET_KEY - JWT密钥（生产环境必须修改）"
echo ""
echo "配置文件位置: backend/.env"

