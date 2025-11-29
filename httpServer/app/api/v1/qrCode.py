from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO
from app.schemas.event import EventBase
from app.schemas.user import UserBase
from app.core.security import get_current_user
from app.core.config import SECRET_KEY
from app.core.config import qr_window_seconds
from app.core.config import qrcode_url
import hashlib
import time

router = APIRouter(prefix="/qrcode", tags=["二维码"])

# @router.get("/generate")
# async def generate_qrcode(user: str,
#                           event: str,
#                           action: str='checkin'):
#     """
#     生成二维码
#     """
#     qr_data = qrcode_url+f"{action}?uid={user}&event_id={event}"
#
#     #生成二维码
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#          )
#
#     qr.add_data(qr_data)
#     qr.make(fit=True)
#     img = qr.make_image(fill_color="black", back_color="white")
#
#     #转换为字节流返回
#     img_buffer = BytesIO()
#     img.save(img_buffer, format='PNG')
#     img_buffer.seek(0)
#     return StreamingResponse(img_buffer, media_type="image/png")

def is_timestamp_valid(timestamp: str, window: int = qr_window_seconds) -> bool:
    """
    判断二维码时间戳是否在有效期内
    :param timestamp: 二维码中的时间戳（字符串类型）
    :param window: 有效时间窗口（秒），默认5分钟
    :return: 是否有效
    """
    try:
        ts = int(timestamp)
        now = int(time.time())
        return abs(now - ts) <= window  # 判断时间戳是否在有效期内
    except Exception:
        return False

def verify_token(event_id: str, token: str, timestamp: str) -> bool:
    """
    校验二维码中的 token 是否有效
    """
    secret_key = SECRET_KEY
    token_string = f"{event_id}{timestamp}{secret_key}"
    expected_token = hashlib.md5(token_string.encode()).hexdigest()
    return expected_token == token

#带安全验证的实现
def generate_secure_token(event:str)->tuple:
    """
    生成安全令牌
    :param event: 石光活动id
    :return: 安全令牌
    """
    timestamp = str(int(time.time()))
    secret_key = SECRET_KEY
    token_string=f"{event}{timestamp}{secret_key}"
    return hashlib.md5(token_string.encode()).hexdigest(), timestamp

@router.get("/generate")
async def generate_secure_qr(
        event_id: str,
        user: UserBase = Depends(get_current_user),
        action: str = "checkin"
):
    """
    生成带安全验证的二维码
    :param event_id: 石光活动id
    :param user: UserBase
    :param action: 签到或签退
    :return: 字节流二维码
    """

    if user.uid is None:
        raise HTTPException(status_code=400, detail="用户未登录")
    try:
        # 生成安全令牌
        token, timestamp = generate_secure_token(event_id)
        # 生成二维码
        qr_data = qrcode_url + f"{action}?uid={user.uid}&event_id={event_id}&token={token}&timestamp={timestamp}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # 转换为字节流返回
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return StreamingResponse(img_buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"生成安全令牌失败:{e}")
    
@router.get("/checkin")
async def checkin_qr(
        uid: str,
        event_id: str,
        token: str,
        timestamp: str
):
    """
    签到或签退二维码验证接口
    :param uid: 用户id
    :param event_id: 石光活动id
    :param token: 安全令牌
    :param timestamp: 时间戳
    :return: 验证结果
    """
    # TODO: 验证UID是否为活动管理员

    # 验证时间戳是否有效
    if not is_timestamp_valid(timestamp):
        raise HTTPException(status_code=400, detail="二维码已过期")

    # 验证 token 是否有效
    if not verify_token(event_id, token, timestamp):
        raise HTTPException(status_code=400, detail="无效的二维码")
    
    # TODO: 在此处添加签到逻辑，例如记录数据库等

    return {"message": "二维码验证通过", "uid": uid, "event_id": event_id}

@router.get("/checkout")
async def checkout_qr(
        uid: str,
        event_id: str,
        token: str,
        timestamp: str
):
    """
    签到或签退二维码验证接口
    :param uid: 用户id
    :param event_id: 石光活动id
    :param token: 安全令牌
    :param timestamp: 时间戳
    :return: 验证结果
    """
    # TODO: 验证UID是否为活动管理员

    # 验证时间戳是否有效
    if not is_timestamp_valid(timestamp):
        raise HTTPException(status_code=400, detail="二维码已过期")

    # 验证 token 是否有效
    if not verify_token(event_id, token, timestamp):
        raise HTTPException(status_code=400, detail="无效的二维码")
    
    # TODO: 在此处添加签退逻辑，例如记录数据库等

    return {"message": "二维码验证通过", "uid": uid, "event_id": event_id}



