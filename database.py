from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json

# Tạo engine kết nối PostgreSQL
engine = create_engine('postgresql://minhdangpy134:minhdang@localhost:5432/blogcuniu')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Database:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def save_profile(self, profile_data):
        with self.SessionLocal() as session:
            # Chuyển đổi tên trường từ camelCase sang snake_case
            db_profile = {
                'name': profile_data.get('name', ''),
                'nickname': profile_data.get('nickname', ''),
                'about': profile_data.get('about', ''),
                'slogan': profile_data.get('slogan', ''),
                'facebook_link': profile_data.get('facebookLink', ''),
                'instagram_link': profile_data.get('instagramLink', ''),
                'tiktok_link': profile_data.get('tiktokLink', ''),
                'locket_link': profile_data.get('locketLink', ''),
                'phone': profile_data.get('phone', ''),
                'avatar_base64': profile_data.get('avatar_base64', '')
            }
            
            # Kiểm tra xem đã có profile chưa
            result = session.execute(text("SELECT id FROM profile LIMIT 1"))
            profile = result.fetchone()
            
            if profile:
                # Update profile hiện tại
                session.execute(
                    text("""
                        UPDATE profile 
                        SET name = :name,
                            nickname = :nickname,
                            about = :about,
                            slogan = :slogan,
                            facebook_link = :facebook_link,
                            instagram_link = :instagram_link,
                            tiktok_link = :tiktok_link,
                            locket_link = :locket_link,
                            phone = :phone,
                            avatar_base64 = :avatar_base64
                        WHERE id = :id
                    """),
                    {**db_profile, 'id': profile[0]}
                )
            else:
                # Tạo profile mới
                session.execute(
                    text("""
                        INSERT INTO profile 
                        (name, nickname, about, slogan, facebook_link, instagram_link, tiktok_link, locket_link, phone, avatar_base64)
                        VALUES 
                        (:name, :nickname, :about, :slogan, :facebook_link, :instagram_link, :tiktok_link, :locket_link, :phone, :avatar_base64)
                    """),
                    db_profile
                )
            
            session.commit()

    def get_profile(self):
        with self.SessionLocal() as session:
            result = session.execute(text("SELECT * FROM profile LIMIT 1"))
            profile = result.fetchone()
            
            if profile:
                return {
                    'name': profile[1],
                    'nickname': profile[2],
                    'about': profile[3],
                    'slogan': profile[4],
                    'facebookLink': profile[5],
                    'instagramLink': profile[6],
                    'tiktokLink': profile[7],
                    'locketLink': profile[8],
                    'phone': profile[9],
                    'avatar_base64': profile[10] if len(profile) > 10 else ''
                }
            return None

# Sử dụng:
if __name__ == "__main__":
    db = Database()
    try:
        # Test lấy profile
        profile = db.get_profile()
        print("Profile:", profile)

        # Test lưu profile
        test_profile = {
            "name": "Test Name",
            "nickname": "Test Nick",
            "about": "Test About",
            "slogan": "Test Slogan",
            "facebookLink": "https://facebook.com/test",
            "instagramLink": "https://instagram.com/test",
            "tiktokLink": "https://tiktok.com/test",
            "locketLink": "https://locket.com/test",
            "phone": "0123456789"
        }
        db.save_profile(test_profile)
        print("Đã lưu profile thành công!")
    finally:
        pass 