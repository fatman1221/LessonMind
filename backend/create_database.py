"""
创建数据库脚本
"""
import pymysql
from config import settings

try:
    # 连接到MySQL服务器（不指定数据库）
    connection = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        charset='utf8mb4'
    )
    
    with connection.cursor() as cursor:
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ 数据库 '{settings.DB_NAME}' 创建成功！")
    
    connection.commit()
    connection.close()
    
    print("✅ 数据库初始化完成！")
    print("现在可以启动服务了：python main.py")
    
except Exception as e:
    print(f"❌ 数据库创建失败: {str(e)}")
    print("\n请检查：")
    print("1. MySQL服务是否已启动")
    print("2. .env 文件中的数据库配置是否正确")
    print("3. 数据库用户是否有创建数据库的权限")

