import io
import os
import torch
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.models import NeuralStyleTransfer
from src.utils import ImageHandler
from src.criterion import Criterion
from PIL import Image
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

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = NeuralStyleTransfer().to(device)
criterion = Criterion()
image_handler = ImageHandler()

app.mount("/static", StaticFiles(directory="../frontend/build/static"), name="static")

class TrainRequest(BaseModel):
    content_image_path: str
    style_image_path: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Neural Style Transfer API!"}

@app.post("/upload/")
async def upload(content: UploadFile = File(...), style: UploadFile = File(...)):
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
    return await train(train_request)

@app.post("/train/")
async def train(request: TrainRequest):
    # Baca gambar dari path yang diberikan
    content_image = image_handler.load_image(request.content_image_path, image_handler.transform).to(device)
    style_image = image_handler.load_image(request.style_image_path, image_handler.transform).to(device)

    output = content_image.clone()
    output.requires_grad = True
    optimizer = optim.AdamW([output], lr=0.05)

    # Ambil fitur dari model
    content_features = model(content_image, layers=["4", "8"])
    style_features = model(style_image, layers=["4", "8"])

    max_epochs = 2500
    print(f'---------------------start training---------------------')
    for epoch in range(1, max_epochs+1):
        output_features = model(output, layers=["4", "8"])
        loss = criterion.criterion(content_features, style_features, output_features, output_features, style_weight=1e6)
        loss.backward()
        
        optimizer.step()
        optimizer.zero_grad()
        
        if epoch % 100 == 0:
            print(f"Epoch: {epoch:5} | Loss: {loss.item():.5f}")
            # _ = image_handler.draw_styled_image(output)
        if epoch == 800 or epoch == 1600 or epoch == 2500:
            output_image_path = f"outputs/output_epoch_{epoch}.png"
            image_handler.save_image(output, output_image_path)
            generated_image_name = f"output_epoch_{epoch}.png"

    return JSONResponse(content={"message": "Training completed!", "generated_image_name": generated_image_name})
    
@app.get("/outputs/{image_name}")
async def get_image(image_name: str):
    image_path = os.path.join("outputs", image_name)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found"}