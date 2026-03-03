from pyodbc import Connection
from core.security import Security

class AuthController:
    @staticmethod
    def login(db: Connection, username: str, password: str):
        cursor = db.cursor()
        
        # 1. Chỉ lấy thông tin cơ bản và Password để kiểm tra
        cursor.execute("""
            SELECT ID, FullName, Password 
            FROM Employees 
            WHERE FullName = ?
        """, (username,))
        
        user = cursor.fetchone()
        
        # 2. Kiểm tra mật khẩu bằng hàm Security đã nâng cấp
        if user and Security.verify_password(password, user.Password):
            user_id = user.ID
            
            # 3. Lấy danh sách PermCode từ bảng mới EmployeePermissions
            cursor.execute("SELECT PermCode FROM EmployeePermissions WHERE EmployeeID = ?", (user_id,))
            # Gom thành chuỗi "perm1,perm2" để Frontend (localStorage) không bị lỗi split(',')
            perms_list = [row.PermCode for row in cursor.fetchall()]
            perms_str = ",".join(perms_list)

            return {
                "status": "success",
                "user": {
                    "id": user_id,
                    "name": user.FullName,
                    "perms": perms_str
                }
            }
            
        return {
            "status": "error", 
            "message": "Tài khoản hoặc mật khẩu không đúng!"
        }
