from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO
from app.schemas.event import EventBase
from app.schemas.user import UserBase

from app.core.config import qrcode_url
import hashlib
import time

router = APIRouter(prefix="/qrcode", tags=["二维码"])

@router.get("/generate")
async def generate_qrcode(user: str,
                          event: str,
                          action: str='checkin'):
    """
    生成二维码
    """
    qr_data = qrcode_url+f"{action}?uid={user}&event_id={event}"

    #生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
         )

    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    #转换为字节流返回
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return StreamingResponse(img_buffer, media_type="image/png")

#带安全验证的实现
def generate_secure_token(user:str,event:str)->str:
    """生成安全令牌"""
    timestamp = str(int(time.time()))
    secret_key = "your_secret_key"
    token_string=f"{user}{event}{timestamp}{secret_key}"
    return hashlib.md5(token_string.encode()).hexdigest()




