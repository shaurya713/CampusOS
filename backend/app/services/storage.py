import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from app.config import get_settings

IMAGE_TYPES={"image/jpeg","image/png","image/webp"}; VIDEO_TYPES={"video/mp4","video/quicktime","video/webm"}
async def save_upload(file:UploadFile,kind:str)->str:
    settings=get_settings(); allowed=IMAGE_TYPES if kind=="image" else VIDEO_TYPES; limit=settings.max_image_size if kind=="image" else settings.max_video_size
    if file.content_type not in allowed: raise HTTPException(415,"Unsupported file type")
    content=await file.read()
    if not content or len(content)>limit: raise HTTPException(413,"File exceeds the permitted size")
    suffix=Path(file.filename or "").suffix.lower()
    if suffix not in ({".jpg",".jpeg",".png",".webp"} if kind=="image" else {".mp4",".mov",".webm"}):raise HTTPException(415,"Invalid file extension")
    target=settings.upload_dir/kind;target.mkdir(parents=True,exist_ok=True);name=f"{uuid.uuid4()}{suffix}";(target/name).write_bytes(content)
    return f"/uploads/{kind}/{name}"
