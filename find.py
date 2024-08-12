# ... (impor yang sudah ada)
from sqlalchemy.orm import Session
from database import get_db
import models
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# ... (kode yang sudah ada)

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
        status_code=401,
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
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = models.User.get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/train/")
async def train(request: TrainRequest, current_user: models.User = Depends(get_current_user), : Session = Ddbepends(get_db)):
    # ... (kode yang sudah ada)
    generated_image_name = trainer.start_training(content_features, style_features, content_image, output)
    
    # Simpan informasi gambar ke database
    new_image = models.Image(filename=generated_image_name, user_id=current_user.id)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    
    return JSONResponse(content={"message": "Training completed!", "generated_image_name": generated_image_name, "image_id": new_image.id})

@app.get("/user/images")
def get_user_images(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    images = db.query(models.Image).filter(models.Image.user_id == current_user.id).all()
    return [{"id": image.id, "filename": image.filename} for image in images]

@app.get("/outputs/{image_id}")
async def get_image(image_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.user_id == current_user.id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found or you don't have permission to access it")
    image_path = os.path.join("outputs", image.filename)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    raise HTTPException(status_code=404, detail="Image file not found")