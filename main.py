import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from database import write_system_log

from core.config import settings
from routers.auth_rt import router as auth_router
from routers.employee_rt import router as employee_router
from routers.department_rt import router as department_router
from routers.permission_rt import router as perm_router

app = FastAPI(title=settings.PROJECT_NAME)

# --- QUAN TRỌNG: THỨ TỰ MIDDLEWARE ---

# 1. Log Middleware (Khai báo trước để bọc bên ngoài Session)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Cho request đi qua các middleware khác và router trước
    response = await call_next(request)
    
    # Chỉ ghi log sau khi đã có kết quả (đảm bảo SessionMiddleware đã chạy xong)
    try:
        user_name = request.session.get("user_name", "Anonymous")
        ip = request.client.host
        path = request.url.path
        method = request.method
        
        # Gọi hàm ghi log từ database.py
        write_system_log(user_name, method, path, response.status_code, ip)
    except Exception:
        # Bỏ qua nếu request không có session (như file tĩnh)
        pass
        
    return response

# 2. SessionMiddleware (Khai báo SAU log_middleware để nó nằm "gần" Router hơn)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# --- CẤU HÌNH STATIC & TEMPLATES ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 3. Route Gốc
@app.get("/")
async def index(request: Request):
    if 'user_id' not in request.session:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})

# 4. Đăng ký Routers
app.include_router(auth_router)
app.include_router(employee_router, prefix="/employees", tags=["Nhân viên"])
app.include_router(department_router, prefix="/departments", tags=["Phòng ban"])
app.include_router(perm_router, prefix="/permissions", tags=["Phân quyền"])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6066))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
