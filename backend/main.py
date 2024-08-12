import io
import os
import torch
from fastapi import FastAPI, UploadFile, File, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.models_db import User, Image
from app.database import engine, get_db, Base
from src.models import NeuralStyleTransfer

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from src.utils import ImageHandler
from src.training import Trainer
from PIL import Image as PILImage
from torch import optim

app = FastAPI()

# Konfigurasi CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = NeuralStyleTransfer().to(device)
image_handler = ImageHandler()
trainer = Trainer()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.mount("/static", StaticFiles(directory="../frontend/build/static"), name="static")

class TrainRequest(BaseModel):
    content_image_path: str
    style_image_path: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Neural Style Transfer API!"}

@app.post("/upload/")
async def upload(
    content: UploadFile = File(...),
    style: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    os.makedirs("uploads", exist_ok=True)

    content_image_path = f"uploads/content_{content.filename}"
    with open(content_image_path, "wb") as f:
        f.write(await content.read())

    style_image_path = f"uploads/style_{style.filename}"
    with open(style_image_path, "wb") as f:
        f.write(await style.read())

    train_request = TrainRequest(
        content_image_path=content_image_path,
        style_image_path=style_image_path
    )
    return await train(train_request, current_user=current_user, db=db)

@app.post("/train/")
async def train(request: TrainRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Baca gambar dari path yang diberikan
    content_image = image_handler.load_image(request.content_image_path, image_handler.transform).to(device)
    style_image = image_handler.load_image(request.style_image_path, image_handler.transform).to(device)

    output = content_image.clone()
    output.requires_grad = True

    # Ambil fitur dari model
    content_features = model(content_image, layers=["4", "8"])
    style_features = model(style_image, layers=["4", "8"])

    generated_image_name = trainer.start_training(content_features, style_features, content_image, output)
    new_image = Image(filename=generated_image_name, user_id=current_user.id)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return JSONResponse(content={"message": "Training completed!", "generated_image_name": generated_image_name})
    
@app.get("/user/images")
def get_user_images(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    images = db.query(Image).filter(Image.user_id == current_user.id).all()
    return [{"id": image.id, "filename": image.filename} for image in images]

@app.get("/outputs/{filename}")
async def get_image(filename: str, current_user: User = Depends(get_current_user)):
    file_path = os.path.join("outputs", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}, 404

#---------------------------------------login api---------------------------------------#

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = User.get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}