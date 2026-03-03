from pyodbc import Connection
from schemas.department import DepartmentSaveRequest

class DepartmentController:
    @staticmethod
    def get_all(db: Connection):
        cursor = db.cursor()
        cursor.execute("SELECT DeptID, DeptName FROM Departments ORDER BY DeptName")
        # Cách lấy tên cột chuẩn nhất cho FastAPI JSON
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    @staticmethod
    def save(db: Connection, data: DepartmentSaveRequest):
        cursor = db.cursor()
        dept_name = data.DeptName.strip()
        dept_id = data.DeptID

        # 1. Kiểm tra trùng tên
        if dept_id:
            cursor.execute("SELECT COUNT(*) FROM Departments WHERE DeptName = ? AND DeptID != ?", (dept_name, dept_id))
        else:
            cursor.execute("SELECT COUNT(*) FROM Departments WHERE DeptName = ?", (dept_name,))
        
        if cursor.fetchone()[0] > 0:
            return False, "Tên phòng ban đã tồn tại!"

        # 2. Thực hiện Lưu/Cập nhật
        try:
            if dept_id:
                cursor.execute("UPDATE Departments SET DeptName=? WHERE DeptID=?", (dept_name, dept_id))
            else:
                cursor.execute("INSERT INTO Departments (DeptName) VALUES (?)", (dept_name,))
            db.commit()
            return True, "Lưu thành công"
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def delete(db: Connection, dept_id: int):
        cursor = db.cursor()
        # Kiểm tra ràng buộc nhân viên
        cursor.execute("SELECT COUNT(*) FROM Employees WHERE IdDepartment = ?", (dept_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return False, f"Không thể xóa! Đang có {count} nhân viên thuộc bộ phận này."
        
        cursor.execute("DELETE FROM Departments WHERE DeptID = ?", (dept_id,))
        db.commit()
        return True, "Xóa bộ phận thành công."
