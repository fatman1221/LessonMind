@echo off
echo Starting AI Teacher Prep System Backend...

REM 激活虚拟环境（如果使用）
REM call venv\Scripts\activate

REM 安装依赖
pip install -r requirements.txt

REM 运行服务
python main.py

pause

