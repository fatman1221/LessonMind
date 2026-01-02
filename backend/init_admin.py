"""
创建初始管理员账号
"""
from database import SessionLocal
from models import User
from api.auth import get_password_hash

def create_admin_user():
    """创建默认管理员账号"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员账号
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("⚠️  管理员账号已存在！")
            print(f"   用户名: admin")
            print("   请使用现有账号登录，或修改密码")
            return
        
        # 创建默认管理员账号
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ 默认管理员账号创建成功！")
        print("=" * 40)
        print("   用户名: admin")
        print("   密码: admin123")
        print("   邮箱: admin@example.com")
        print("=" * 40)
        print("⚠️  请登录后立即修改密码！")
        
    except Exception as e:
        print(f"❌ 创建管理员账号失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()

