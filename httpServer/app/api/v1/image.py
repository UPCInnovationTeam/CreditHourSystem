from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
from datetime import datetime
import uuid
import platform


router = APIRouter(prefix="/image", tags=["石光活动图片"])

if platform.system() == "Windows":
    # 设置上传文件夹
    UPLOAD_FOLDER = "uploaded_images"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
elif platform.system() == "Linux":
    UPLOAD_FOLDER = "/www/images/"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片接口
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 生成唯一文件名
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 返回文件信息
        file_size = os.path.getsize(file_path)
        return JSONResponse(
            status_code=200,
            content={
                "filename": unique_filename,
                "original_filename": file.filename,
                "content_type": file.content_type,
                "size": file_size,
                "upload_time": datetime.now().isoformat(),
                "saved_path": file_path
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

@router.get("/list-images/")
async def list_images():
    """
    列出所有已上传的图片
    """
    try:
        files = os.listdir(UPLOAD_FOLDER)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
        return {"images": image_files, "count": len(image_files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@router.get("/image/{filename}")
async def get_image_info(filename: str):
    """
    获取特定图片信息
    """
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_stats = os.stat(file_path)
    return {
        "filename": filename,
        "size": file_stats.st_size,
        "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
        "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
    }

@router.get("/images/{filename}")
async def get_image(filename: str):
     """
    根据文件名获取图片文件内容

    :param filename: 请求的图片文件名
    :return: 图片文件响应或错误信息
    """
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path)


