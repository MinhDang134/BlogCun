from fastapi import FastAPI, File, UploadFile, HTTPException  # Thêm File và UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles  # Thêm cái này để phục vụ file tĩnh
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import Database, engine  # Giả sử database.py của cháu vẫn ổn
from sqlalchemy import text
import os  # Thư viện để làm việc với thư mục và file
import shutil  # Thư viện để copy file

app = FastAPI()

# --- Cấu hình CORS (giữ nguyên) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Tạo thư mục để lưu ảnh (QUAN TRỌNG) ---
# Thư mục này sẽ nằm cùng cấp với file Python FastAPI của cháu
UPLOAD_DIRECTORY = "./static/images"  # Đặt tên thư mục là static/images
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)  # Tạo thư mục nếu chưa có

# --- Cho phép server phục vụ các file trong thư mục static (QUAN TRỌNG) ---
# Để trình duyệt có thể xem được ảnh sau khi upload
app.mount("/static", StaticFiles(directory="static"), name="static")

db = Database()  # Giả sử db của cháu vẫn dùng được


# --- Model Profile (XEM XÉT LẠI CHỖ AVATAR) ---
class ProfileModel(BaseModel):
    name: str = ""
    nickname: str = ""
    about: str = ""
    slogan: str = ""
    facebookLink: str = ""
    instagramLink: str = ""
    tiktokLink: str = ""
    locketLink: str = ""
    phone: str = ""
    # Cháu nên đổi cái này thành avatarUrl để lưu đường dẫn ảnh nhé
    # avatar_base64: str = "" # Dòng này có thể sẽ không cần nữa nếu cháu dùng cách upload file
    avatarUrl: str = ""  # Đổi thành avatarUrl kiểu string


# --- API Endpoint cho Profile (giữ nguyên, nhưng xem lại ProfileModel) ---
@app.post("/profile")
def save_profile(profile: ProfileModel):  # ProfileModel giờ nên có avatarUrl
    # Khi lưu profile, cháu sẽ lưu profile.avatarUrl (là đường dẫn ảnh)
    db.save_profile(profile.dict())
    return {"success": True}


@app.get("/profile")
def get_profile():
    profile_data = db.get_profile()  # Đổi tên biến để tránh trùng với tên hàm
    # Nếu profile_data là None hoặc không có avatarUrl, cháu có thể đặt giá trị mặc định
    if profile_data and not profile_data.get("avatarUrl"):  # Kiểm tra nếu avatarUrl rỗng
        profile_data[
            "avatarUrl"] = 'https://api.dicebear.com/7.x/avataaars/svg?seed=Cun&backgroundColor=b6e3f4'  # Ảnh mặc định
    elif not profile_data:  # Nếu không có profile nào cả
        # Trả về cấu trúc rỗng với avatar mặc định để frontend không lỗi
        profile_data = {
            "name": "", "nickname": "", "about": "", "slogan": "",
            "facebookLink": "", "instagramLink": "", "tiktokLink": "",
            "locketLink": "", "phone": "",
            "avatarUrl": 'https://api.dicebear.com/7.x/avataaars/svg?seed=Cun&backgroundColor=b6e3f4'
        }
    return {"profile": profile_data}


# --- CỬA MỚI ĐỂ UPLOAD AVATAR (THÊM VÀO ĐÂY) ---
@app.post("/upload-avatar/")
async def create_upload_avatar(file: UploadFile = File(...)):
    try:

        abs_upload_dir = os.path.abspath(UPLOAD_DIRECTORY)
        file_path = os.path.join(abs_upload_dir, file.filename)

        print(f"--- THÔNG BÁO TỪ FASTAPI (UPLOAD AVATAR) ---")
        print(f"1. FastAPI đang chạy từ thư mục (CWD): {os.getcwd()}")
        print(f"2. UPLOAD_DIRECTORY (tương đối) được đặt là: {UPLOAD_DIRECTORY}")
        print(f"3. Đường dẫn tuyệt đối của thư mục upload (abs_upload_dir) là: {abs_upload_dir}")
        print(f"4. Sẽ cố gắng tạo thư mục (nếu chưa có): {abs_upload_dir}")
        print(f"5. Tên file nhận được: {file.filename}")
        print(f"6. Đường dẫn đầy đủ đến file sẽ lưu (file_path) là: {file_path}")

        os.makedirs(abs_upload_dir, exist_ok=True)
        print(f"7. Đã kiểm tra/tạo thư mục: {abs_upload_dir}")

        # Lưu file ảnh vào thư mục UPLOAD_DIRECTORY
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"8. Đã lưu file thành công vào: {file_path}")  # In ra nếu lưu thành công

        # Đường dẫn URL mà trình duyệt có thể dùng để xem ảnh
        file_url = f"/static/images/{file.filename}"  # Đảm bảo dòng này đúng
        print(f"9. URL trả về cho trình duyệt sẽ là: {file_url}")
        print(f"--- KẾT THÚC THÔNG BÁO TỪ FASTAPI (UPLOAD AVATAR) ---")

        return {"avatarUrl": file_url, "filename": file.filename}

    except Exception as e:
        print(f"--- LỖI TRONG FASTAPI KHI UPLOAD FILE ---")
        print(f"FastAPI đang chạy từ thư mục (CWD): {os.getcwd()}")
        print(f"Lỗi chi tiết khi upload: {e}")
        print(f"---------------------------------------")
        raise HTTPException(status_code=500, detail=f"Không thể upload file: {str(e)}")


# ... phần code còn lại của cháu ...

try:
    with engine.connect() as conn:
        # Nếu cháu muốn bỏ cột avatar_base64 (CẨN THẬN: sẽ mất dữ liệu cột đó nếu có)
        # try:
        #     conn.execute(text("ALTER TABLE profile DROP COLUMN avatar_base64"))
        # except Exception as e_drop:
        #     print(f"Note: Could not drop avatar_base64 column (maybe it doesn't exist or has dependencies): {e_drop}")

        conn.execute(text("ALTER TABLE profile ADD COLUMN IF NOT EXISTS avatarUrl TEXT"))  # Thêm cột avatarUrl
        conn.commit()
        print("Cột avatarUrl đã được kiểm tra/thêm vào bảng profile.")
except Exception as e:
    print(f"Lỗi khi sửa bảng profile: {e}")