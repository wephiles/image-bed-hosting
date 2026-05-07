"""
主应用
"""

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os

from app.database import SessionLocal, engine, Base
from app import models, crud, auth, utils

# 创建表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Image Hosting")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or not auth.verify_password(form_data.password):
        raise HTTPException(400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": "admin"})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/upload")
async def upload_image(
        request: Request,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        token: str = Depends(auth.verify_token)
):
    contents = await file.read()
    if not utils.allowed_file_size(len(contents)):
        raise HTTPException(413, detail="File too large (max 10 MB)")

    filename = utils.generate_filename(file.filename)
    utils.save_image(contents, filename)
    original_path = os.path.join(utils.UPLOAD_DIR, filename)
    utils.create_thumbnail(original_path, filename)

    image = crud.create_image(db, filename, file.filename, len(contents))

    host = request.headers.get("host", "localhost:8000")
    base_url = f"http://{host}"
    return {
        "id": image.id,
        "filename": filename,
        "original_name": image.original_name,
        "size": image.size,
        "url": f"{base_url}/uploads/originals/{filename}",
        "thumb_url": f"{base_url}/uploads/thumbnails/{filename}",
        "markdown": f"![{image.original_name}]({base_url}/uploads/originals/{filename})"
    }


@app.get("/api/images")
def list_images(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), token: str = Depends(auth.verify_token)):
    images = crud.get_images(db, skip=skip, limit=limit)
    result = []
    for img in images:
        result.append({
            "id": img.id,
            "filename": img.filename,
            "original_name": img.original_name,
            "size": img.size,
            "upload_time": img.upload_time.isoformat(),
            "thumb_url": f"/uploads/thumbnails/{img.filename}",
            "url": f"/uploads/originals/{img.filename}"
        })
    return result


@app.delete("/api/images/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db), token: str = Depends(auth.verify_token)):
    success = crud.delete_image(db, image_id)
    if not success:
        raise HTTPException(404, detail="Image not found")
    return {"ok": True}


@app.get("/api/image/{filename}")
def serve_image(filename: str):
    return FileResponse(os.path.join(utils.UPLOAD_DIR, filename))


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
