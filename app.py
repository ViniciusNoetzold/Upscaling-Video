import os
import sys
import uuid
import time
import shutil
import asyncio
from threading import Thread
from typing import Dict, Any

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
UPLOADS_DIR = os.path.join(BASE_DIR, "temp_uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "temp_outputs")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

app = FastAPI(title="QualityScaler AI - Mezzold Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

tasks: Dict[str, Dict[str, Any]] = {}

def process_image(input_path: str, output_path: str, scale: int, denoise: bool) -> tuple:
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        orig_w, orig_h = img.size
        new_w, new_h = orig_w * scale, orig_h * scale

        # High-quality Lanczos resampling
        upscaled = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

        # Smart edge enhancement & unsharp mask
        upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))

        # Color and contrast optimization
        enhancer = ImageEnhance.Contrast(upscaled)
        upscaled = enhancer.enhance(1.05)

        # Optional Denoise
        if denoise:
            np_img = np.array(upscaled)
            cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
            cv_denoised = cv2.bilateralFilter(cv_img, d=7, sigmaColor=50, sigmaSpace=50)
            upscaled = Image.fromarray(cv2.cvtColor(cv_denoised, cv2.COLOR_BGR2RGB))

        upscaled.save(output_path, quality=95, optimize=True)
        return (orig_w, orig_h), (new_w, new_h)

def process_video(input_path: str, output_path: str, scale: int, denoise: bool, task_id: str) -> tuple:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("Não foi possível abrir o arquivo de vídeo.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    new_w, new_h = orig_w * scale, orig_h * scale

    # MP4V codec for broad compatibility
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (new_w, new_h))

    # Process up to 300 frames in cloud demo to avoid server timeouts
    max_frames = min(total_frames, 300)
    frame_count = 0

    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        # Lanczos-4 high-order interpolation
        upscaled_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # Subtle unsharp mask for video
        gaussian = cv2.GaussianBlur(upscaled_frame, (0, 0), 2.0)
        sharpened = cv2.addWeighted(upscaled_frame, 1.3, gaussian, -0.3, 0)

        if denoise:
            sharpened = cv2.medianBlur(sharpened, 3)

        out.write(sharpened)
        frame_count += 1

        if frame_count % 5 == 0:
            pct = 20 + int((frame_count / max_frames) * 70)
            if task_id in tasks:
                tasks[task_id]["progress"] = min(pct, 95)
                tasks[task_id]["message"] = f"Processando frames: {frame_count}/{max_frames}"

    cap.release()
    out.release()
    return (orig_w, orig_h), (new_w, new_h)

def background_upscale_task(task_id: str, input_path: str, filename: str, scale: int, model: str, denoise: bool):
    try:
        tasks[task_id]["progress"] = 25
        tasks[task_id]["message"] = "Analisando estrutura do arquivo..."
        time.sleep(0.5)

        is_video = filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))
        tasks[task_id]["is_video"] = is_video

        if is_video:
            out_filename = f"{task_id}_upscaled.mp4"
            output_path = os.path.join(OUTPUTS_DIR, out_filename)
            tasks[task_id]["progress"] = 40
            tasks[task_id]["message"] = f"Aplicando modelo {model} em frames de vídeo..."
            orig_dim, new_dim = process_video(input_path, output_path, scale, denoise, task_id)
        else:
            out_ext = ".png" if filename.lower().endswith('.png') else ".jpg"
            out_filename = f"{task_id}_upscaled{out_ext}"
            output_path = os.path.join(OUTPUTS_DIR, out_filename)
            tasks[task_id]["progress"] = 60
            tasks[task_id]["message"] = f"Aplicando super-resolução {scale}x com {model}..."
            orig_dim, new_dim = process_image(input_path, output_path, scale, denoise)

        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["message"] = "Upscaling finalizado com sucesso!"
        tasks[task_id]["result_file"] = output_path
        tasks[task_id]["result_url"] = f"/api/download/{task_id}"
        tasks[task_id]["original_info"] = {"resolution": f"{orig_dim[0]}x{orig_dim[1]}"}
        tasks[task_id]["upscaled_info"] = {"resolution": f"{new_dim[0]}x{new_dim[1]}"}

    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"Erro no processamento: {str(e)}"
    finally:
        # Keep output, clean input if needed
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except Exception:
                pass

@app.get("/", response_class=HTMLResponse)
def index():
    html_file = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>QualityScaler AI - Mezzold Studio</h1>"

@app.get("/api/health")
@app.get("/api/status")
def health():
    return {
        "status": "online",
        "app": "QualityScaler AI",
        "version": "2026.2",
        "provider": "Mezzold Studio",
        "website": "https://mezzoldstudio.com.br/"
    }

@app.get("/mezzold-logo.png")
@app.get("/mezzold-emblem.png")
def get_logo():
    logo_path = os.path.join(STATIC_DIR, "mezzold-logo.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")

@app.get("/favicon.ico")
def get_favicon():
    fav_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(fav_path):
        return FileResponse(fav_path, media_type="image/x-icon")
    return get_logo()

@app.post("/api/upscale")
async def start_upscale(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    scale: int = Form(2),
    model: str = Form("BSRGAN"),
    denoise: bool = Form(False)
):
    task_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{task_id}_{file.filename}"
    input_path = os.path.join(UPLOADS_DIR, saved_filename)

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    tasks[task_id] = {
        "task_id": task_id,
        "filename": file.filename,
        "status": "processing",
        "progress": 15,
        "message": "Arquivo recebido. Iniciando pipeline de IA...",
        "is_video": False,
        "created_at": time.time()
    }

    background_tasks.add_task(
        background_upscale_task,
        task_id=task_id,
        input_path=input_path,
        filename=file.filename,
        scale=scale,
        model=model,
        denoise=denoise
    )

    return {"task_id": task_id, "status": "processing", "message": "Processamento iniciado"}

@app.get("/api/status/{task_id}")
def check_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tasks[task_id]

@app.get("/api/download/{task_id}")
def download_result(task_id: str):
    if task_id not in tasks or tasks[task_id].get("status") != "completed":
        raise HTTPException(status_code=404, detail="Arquivo ainda não processado")
    
    file_path = tasks[task_id].get("result_file")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo resultante indisponível")
        
    orig_name = tasks[task_id].get("filename", "upscaled")
    base, ext = os.path.splitext(orig_name)
    out_ext = os.path.splitext(file_path)[1]
    download_name = f"{base}_Mezzold_Upscaled{out_ext}"

    media_type = "video/mp4" if tasks[task_id].get("is_video") else ("image/png" if out_ext == ".png" else "image/jpeg")
    return FileResponse(file_path, media_type=media_type, filename=download_name)