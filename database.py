# File: /srv/BLogCun/database.py (hoặc /root/BLogCun/database.py)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# Tạo engine kết nối PostgreSQL
# CHÚ Ý: Tên user trong đây là minhdangpy134, cháu kiểm tra lại xem có đúng không nhé
engine = create_engine('postgresql://minhdangpy134:minhdang@localhost:5432/blogcuniu')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Database:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def save_profile(self, profile_data_from_frontend):
        with self.SessionLocal() as session:
            # Dữ liệu từ frontend có key là camelCase (ví dụ: avatarUrl, facebookLink)
            # Ta sẽ map chúng vào dictionary với key là placeholder cho SQL.
            # Tên placeholder này sẽ được dùng trong câu lệnh SQL.

            # Đặt tên placeholder giống hệt tên cột CSDL cho dễ quản lý
            data_for_sql = {
                'name': profile_data_from_frontend.get('name', ''),
                'nickname': profile_data_from_frontend.get('nickname', ''),
                'about': profile_data_from_frontend.get('about', ''),
                'slogan': profile_data_from_frontend.get('slogan', ''),
                'facebook_link': profile_data_from_frontend.get('facebookLink', ''),
                # Map facebookLink (frontend) -> facebook_link (placeholder)
                'instagram_link': profile_data_from_frontend.get('instagramLink', ''),
                'tiktok_link': profile_data_from_frontend.get('tiktokLink', ''),
                'locket_link': profile_data_from_frontend.get('locketLink', ''),
                'phone': profile_data_from_frontend.get('phone', ''),
                'avatarurl': profile_data_from_frontend.get('avatarUrl', '')
                # Map avatarUrl (frontend) -> avatarurl (placeholder)
            }

            # Giả sử bảng profile luôn chỉ có 1 dòng, hoặc cháu có cơ chế chọn id
            # Nếu bảng trống, mình sẽ INSERT. Nếu có rồi, mình UPDATE.
            # Mình cần một cách để xác định dòng profile duy nhất, ví dụ luôn là id=1 hoặc lấy dòng đầu tiên.
            # Để đơn giản, mình sẽ thử lấy dòng đầu tiên. Nếu không có, sẽ INSERT.

            result = session.execute(text("SELECT id FROM profile ORDER BY id LIMIT 1"))
            existing_profile = result.fetchone()

            if existing_profile:
                # Update profile hiện tại
                # Tên cột trong SQL phải khớp 100% với CSDL (chữ thường/snake_case)
                # Tên placeholder (ví dụ :name, :facebook_link) phải khớp 100% với key trong data_for_sql
                update_query = text("""
                                    UPDATE profile
                                    SET name           = :name,
                                        nickname       = :nickname,
                                        about          = :about,
                                        slogan         = :slogan,
                                        facebook_link  = :facebook_link,
                                        instagram_link = :instagram_link,
                                        tiktok_link    = :tiktok_link,
                                        locket_link    = :locket_link,
                                        phone          = :phone,
                                        avatarurl      = :avatarurl
                                    WHERE id = :id
                                    """)
                # Thêm id vào dictionary data_for_sql để truyền cho câu UPDATE
                data_for_sql_with_id = {**data_for_sql, 'id': existing_profile.id}
                session.execute(update_query, data_for_sql_with_id)
            else:
                # Tạo profile mới (nếu bảng trống)
                # Tên cột trong SQL phải khớp 100% với CSDL
                # Tên placeholder phải khớp 100% với key trong data_for_sql
                insert_query = text("""
                                    INSERT INTO profile
                                    (name, nickname, about, slogan, facebook_link, instagram_link, tiktok_link,
                                     locket_link, phone, avatarurl)
                                    VALUES (:name, :nickname, :about, :slogan, :facebook_link, :instagram_link,
                                            :tiktok_link, :locket_link, :phone, :avatarurl)
                                    """)
                session.execute(insert_query, data_for_sql)

            session.commit()
            print(
                f"[DB SAVE] Đã gọi hàm save_profile. Giá trị cho cột 'avatarurl' trong CSDL là: {data_for_sql.get('avatarurl')}")

    def get_profile(self):
        with self.SessionLocal() as session:
            # SELECT đúng tên cột từ CSDL
            select_query = text("""
                                SELECT id,
                                       name,
                                       nickname,
                                       about,
                                       slogan,
                                       facebook_link,
                                       instagram_link,
                                       tiktok_link,
                                       locket_link,
                                       phone,
                                       avatarurl
                                FROM profile
                                ORDER BY id LIMIT 1
                                """)  # Lấy dòng đầu tiên nếu có nhiều

            profile_row = session.execute(select_query).fetchone()

            if profile_row:
                # Lấy dữ liệu từ CSDL bằng tên thuộc tính (khớp với tên cột đã SELECT)
                avatar_from_db = profile_row.avatarurl if profile_row.avatarurl else ''  # Đảm bảo không phải None

                # Trả về dữ liệu với key là camelCase giống Frontend mong đợi
                profile_for_frontend = {
                    'id': profile_row.id,  # Có thể frontend cũng cần id
                    'name': profile_row.name if profile_row.name else '',
                    'nickname': profile_row.nickname if profile_row.nickname else '',
                    'about': profile_row.about if profile_row.about else '',
                    'slogan': profile_row.slogan if profile_row.slogan else '',
                    'facebookLink': profile_row.facebook_link if profile_row.facebook_link else '',
                    'instagramLink': profile_row.instagram_link if profile_row.instagram_link else '',
                    'tiktokLink': profile_row.tiktok_link if profile_row.tiktok_link else '',
                    'locketLink': profile_row.locket_link if profile_row.locket_link else '',
                    'phone': profile_row.phone if profile_row.phone else '',
                    'avatarUrl': avatar_from_db
                }
                print(
                    f"[DB GET] Đã lấy profile từ CSDL. Giá trị avatarUrl trả về cho frontend là: {profile_for_frontend.get('avatarUrl')}")
                return profile_for_frontend

            print("[DB GET] Không tìm thấy profile nào trong CSDL.")
            return None


# Phần test này cháu có thể chạy riêng file database.py để kiểm tra
if __name__ == "__main__":
    db = Database()
    print("--- Chạy test database.py với CSDL mới nhất ---")
    try:
        print("\n[TEST] Xóa bảng profile cũ (nếu có) và tạo lại bảng profile mới...")
        with db.engine.connect() as connection:
            connection.execute(text("DROP TABLE IF EXISTS profile;"))
            connection.execute(text("""
                                    CREATE TABLE profile
                                    (
                                        id             SERIAL PRIMARY KEY,
                                        name           TEXT DEFAULT '',
                                        nickname       TEXT DEFAULT '',
                                        about          TEXT DEFAULT '',
                                        slogan         TEXT DEFAULT '',
                                        facebook_link  TEXT DEFAULT '',
                                        instagram_link TEXT DEFAULT '',
                                        tiktok_link    TEXT DEFAULT '',
                                        locket_link    TEXT DEFAULT '',
                                        phone          TEXT DEFAULT '',
                                        avatarurl      TEXT DEFAULT ''
                                    );
                                    """))
            connection.commit()
        print("[TEST] Đã tạo lại bảng profile.")

        print("\n[TEST] Đang cố gắng lấy profile ban đầu (sẽ là None vì bảng vừa được tạo lại và trống)...")
        profile_data_from_db = db.get_profile()
        if profile_data_from_db:
            print(
                f"[TEST] Profile lấy được ban đầu: Tên='{profile_data_from_db.get('name')}', Avatar='{profile_data_from_db.get('avatarUrl')}'")
        else:
            print("[TEST] Chính xác! Không có profile nào ban đầu.")

        test_profile_data_frontend = {
            "name": "Cún Siêu Cấp VIP", "nickname": "Cún Pro Max", "about": "Thông tin mới nhất của Cún",
            "slogan": "Slogan đỉnh của chóp!", "facebookLink": "fb.com/cunvip",
            "instagramLink": "ig.com/cunvip", "tiktokLink": "tt.com/cunvip",
            "locketLink": "locket.com/cunvip", "phone": "111222",
            "avatarUrl": "/static/images/cun_vip_avatar.jpg"
        }
        print(
            f"\n[TEST] Đang cố gắng lưu profile test: Tên='{test_profile_data_frontend.get('name')}', Avatar='{test_profile_data_frontend.get('avatarUrl')}'")
        db.save_profile(test_profile_data_frontend)  # Sẽ thực hiện INSERT vì bảng trống
        print("[TEST] Đã gọi hàm lưu profile (thực hiện INSERT)!")

        print("\n[TEST] Đang cố gắng lấy lại profile sau khi INSERT...")
        profile_data_after_save = db.get_profile()
        if profile_data_after_save:
            print(
                f"[TEST] Profile lấy được sau khi INSERT: Tên='{profile_data_after_save.get('name')}', Avatar='{profile_data_after_save.get('avatarUrl')}'")
            if profile_data_after_save.get('avatarUrl') == "/static/images/cun_vip_avatar.jpg" and \
                    profile_data_after_save.get('name') == "Cún Siêu Cấp VIP" and \
                    profile_data_after_save.get('facebookLink') == "fb.com/cunvip":
                print(
                    ">>> [TEST KẾT QUẢ] THÀNH CÔNG: Dữ liệu (bao gồm avatarUrl và các link) đã được INSERT và đọc đúng!")
            else:
                print(
                    ">>> [TEST KẾT QUẢ] THẤT BẠI: Dữ liệu (bao gồm avatarUrl và các link) KHÔNG được INSERT hoặc đọc đúng.")
                print("   Giá trị avatarUrl mong đợi: /static/images/cun_vip_avatar.jpg")
                print("   Giá trị avatarUrl thực tế: ", profile_data_after_save.get('avatarUrl'))
                print("   Giá trị facebookLink mong đợi: fb.com/cunvip")
                print("   Giá trị facebookLink thực tế: ", profile_data_after_save.get('facebookLink'))
        else:
            print("[TEST] Không lấy được profile sau khi INSERT.")

        # Test UPDATE
        updated_profile_data = {
            "name": "Cún Update Rồi",
            "nickname": "Nick Update",
            "avatarUrl": "/static/images/updated_avatar.jpg",
            "facebookLink": "fb.com/cunupdate"
            # Các trường khác sẽ là rỗng nếu không cung cấp, hoặc cháu có thể lấy giá trị cũ rồi cập nhật
        }
        print(
            f"\n[TEST] Đang cố gắng UPDATE profile: Tên='{updated_profile_data.get('name')}', Avatar='{updated_profile_data.get('avatarUrl')}'")
        db.save_profile(updated_profile_data)  # Sẽ thực hiện UPDATE
        print("[TEST] Đã gọi hàm lưu profile (thực hiện UPDATE)!")

        print("\n[TEST] Đang cố gắng lấy lại profile sau khi UPDATE...")
        profile_data_after_update = db.get_profile()
        if profile_data_after_update:
            print(
                f"[TEST] Profile lấy được sau khi UPDATE: Tên='{profile_data_after_update.get('name')}', Avatar='{profile_data_after_update.get('avatarUrl')}'")
            if profile_data_after_update.get('avatarUrl') == "/static/images/updated_avatar.jpg" and \
                    profile_data_after_update.get('name') == "Cún Update Rồi" and \
                    profile_data_after_update.get('facebookLink') == "fb.com/cunupdate":
                print(">>> [TEST KẾT QUẢ UPDATE] THÀNH CÔNG!")
            else:
                print(">>> [TEST KẾT QUẢ UPDATE] THẤT BẠI.")
                print("   Giá trị avatarUrl mong đợi: /static/images/updated_avatar.jpg")
                print("   Giá trị avatarUrl thực tế: ", profile_data_after_update.get('avatarUrl'))
                print("   Giá trị facebookLink mong đợi: fb.com/cunupdate")
                print("   Giá trị facebookLink thực tế: ", profile_data_after_update.get('facebookLink'))
        else:
            print("[TEST] Không lấy được profile sau khi UPDATE.")

    except Exception as e:
        print(f"Lỗi khi test database.py: {e}")