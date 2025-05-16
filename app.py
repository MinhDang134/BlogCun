from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import Database

app = FastAPI()

# Cho phép CORS để frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

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

@app.post("/profile")
def save_profile(profile: ProfileModel):
    db.save_profile(profile.dict())
    return {"success": True}

@app.get("/profile")
def get_profile():
    profile = db.get_profile()
    return {"profile": profile} 