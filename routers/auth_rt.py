from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pyodbc import Connection

from database import get_db
from controllers.auth_ctl import AuthController
from schemas.auth import LoginRequest  # Import Schema vừa tạo

router = APIRouter(prefix="/auth", tags=["Xác thực"])
templates = Jinja2Templates(directory="templates")

# 1. Trang hiển thị Login
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # Nếu đã login rồi thì mới đẩy về trang chủ
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=303)
    
    # Nếu chưa login, CHỈ trả về template, KHÔNG redirect thêm lần nào nữa
    return templates.TemplateResponse("login.html", {"request": request})

# 2. API Login (Sử dụng Schema & Dependency Injection)
@router.post("/api/login")
async def api_login(
    request: Request, 
    data: LoginRequest,                # Dùng Schema thay vì dict
    db: Connection = Depends(get_db)   # Lấy kết nối DB tự động
):
    # Controller giờ nhận thêm tham số 'db' từ router truyền vào
    result = AuthController.login(db, data.username, data.password)
    
    if result["status"] == "success":
        user_data = result["user"]
        request.session["user_id"] = user_data["id"]
        request.session["user_name"] = user_data["name"]
        request.session["permissions"] = user_data["perms"]
        
    return result # FastAPI tự chuyển dict thành JSONResponse

# 3. API Đăng xuất
@router.get("/api/logout")
async def api_logout(request: Request):
    request.session.clear()
    return {"status": "success"}
