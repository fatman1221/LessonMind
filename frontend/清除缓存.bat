@echo off
echo 正在清除 Vite 缓存...
if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo Vite 缓存已清除！
) else (
    echo 没有找到缓存文件
)
echo.
echo 请重新运行: npm run dev

