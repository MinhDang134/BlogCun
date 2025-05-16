import psycopg2
from psycopg2.extras import RealDictCursor
import json

class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                port="5432",
                database="blogcuniu",
                user="minhdangpy134",
                password="minhdang"  # Thay đổi password của bạn ở đây
            )
            self.create_tables()
        except Exception as e:
            print(f"Lỗi kết nối database: {e}")
            raise e

    def create_tables(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS profile (
                        id SERIAL PRIMARY KEY,
                        name TEXT,
                        nickname TEXT,
                        about TEXT,
                        slogan TEXT,
                        facebook_link TEXT,
                        instagram_link TEXT,
                        tiktok_link TEXT,
                        locket_link TEXT,
                        phone TEXT
                    )
                """)
                self.conn.commit()
        except Exception as e:
            print(f"Lỗi tạo bảng: {e}")
            raise e

    def get_profile(self):
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM profile WHERE id = 1")
                row = cur.fetchone()
                
                if row:
                    # Chuyển đổi snake_case sang camelCase
                    profile = {}
                    for k, v in row.items():
                        key = ''.join(word.capitalize() if i else word.lower() 
                                    for i, word in enumerate(k.split('_')))
                        profile[key] = v
                    return profile
                return {}
        except Exception as e:
            print(f"Lỗi lấy profile: {e}")
            raise e

    def save_profile(self, profile_data):
        try:
            # Chuyển đổi camelCase sang snake_case
            data = {}
            for k, v in profile_data.items():
                key = ''.join(['_' + c.lower() if c.isupper() else c for c in k]).lstrip('_')
                data[key] = v

            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO profile (id, name, nickname, about, slogan, 
                                       facebook_link, instagram_link, tiktok_link, 
                                       locket_link, phone)
                    VALUES (1, %(name)s, %(nickname)s, %(about)s, %(slogan)s,
                            %(facebook_link)s, %(instagram_link)s, %(tiktok_link)s,
                            %(locket_link)s, %(phone)s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = %(name)s,
                        nickname = %(nickname)s,
                        about = %(about)s,
                        slogan = %(slogan)s,
                        facebook_link = %(facebook_link)s,
                        instagram_link = %(instagram_link)s,
                        tiktok_link = %(tiktok_link)s,
                        locket_link = %(locket_link)s,
                        phone = %(phone)s
                """, data)
                self.conn.commit()

            # Ghi ra file database.json
            with open('database.json', 'w', encoding='utf-8') as f:
                json.dump({'profile': profile_data}, f, ensure_ascii=False, indent=4)

            return True
        except Exception as e:
            print(f"Lỗi lưu profile: {e}")
            raise e

    def close(self):
        if self.conn:
            self.conn.close()

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
        db.close() 