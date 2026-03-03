import pandas as pd
from io import BytesIO
from pyodbc import Connection
from schemas.employee import EmployeeCreate

class EmployeeController:
    @staticmethod
    def get_all(db: Connection):
        cursor = db.cursor()
        cursor.execute("""
            SELECT E.ID, E.FullName, D.DeptName, E.IdDepartment 
            FROM Employees E LEFT JOIN Departments D ON E.IdDepartment = D.DeptID
        """)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def save(db: Connection, data: EmployeeCreate):
        cursor = db.cursor()
        if data.ID:
            cursor.execute(
                "UPDATE Employees SET FullName=?, IdDepartment=? WHERE ID=?",
                (data.FullName, data.IdDepartment, data.ID),
            )
            db.commit()
            return data.ID
        else:
            sql = """
                SET NOCOUNT ON;
                INSERT INTO Employees (FullName, IdDepartment) VALUES (?, ?);
                SELECT CAST(SCOPE_IDENTITY() AS INT);
            """
            cursor.execute(sql, (data.FullName, data.IdDepartment))
            new_id = cursor.fetchone()[0]
            db.commit()
            return new_id

    @staticmethod
    def delete(db: Connection, emp_id: int):
        cursor = db.cursor()
        cursor.execute("DELETE FROM Employees WHERE ID=?", (emp_id,))
        db.commit()

    @staticmethod
    def export_excel(db: Connection):
        # Tái sử dụng hàm get_all ngay trong cùng 1 connection
        data = EmployeeController.get_all(db)
        df = pd.DataFrame(data)
        df_export = df.rename(columns={"FullName": "Họ và Tên", "DeptName": "Phòng Ban", "ID": "Mã NV"})
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_export[["Mã NV", "Họ và Tên", "Phòng Ban"]].to_excel(writer, index=False)
        output.seek(0)
        return output
    
    @staticmethod
    def get_template_excel(db: Connection):
        cursor = db.cursor()
        cursor.execute("SELECT DeptName FROM Departments")
        departments = [row.DeptName for row in cursor.fetchall()]

        df_template = pd.DataFrame({
            "FullName": ["Nguyễn Văn A", "Trần Thị B"],
            "DepartmentName": (departments[:2] if departments else ["IT", "HR"]),
        })

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_template.to_excel(writer, index=False, sheet_name="Import_Template")
            if departments:
                pd.DataFrame({"Valid_Depts": departments}).to_excel(writer, index=False, sheet_name="Depts")
        output.seek(0)
        return output

    @staticmethod
    def import_excel(db: Connection, file_content: bytes):
        # Đọc dữ liệu từ bytes gửi lên
        df = pd.read_excel(BytesIO(file_content))
        
        cursor = db.cursor()
        # Lấy bản đồ tên -> ID để ánh xạ
        cursor.execute("SELECT DeptID, DeptName FROM Departments")
        dept_map = {row.DeptName: row.DeptID for row in cursor.fetchall()}

        import_data = []
        for _, row in df.iterrows():
            fullname = str(row.get("FullName", "")).strip()
            dept_name = str(row.get("DepartmentName", "")).strip()
            dept_id = dept_map.get(dept_name)

            if fullname and dept_id: # Chỉ import nếu có tên và phòng ban hợp lệ
                import_data.append((fullname, dept_id))

        if import_data:
            try:
                cursor.executemany(
                    "INSERT INTO Employees (FullName, IdDepartment) VALUES (?, ?)", 
                    import_data
                )
                db.commit()
                return len(import_data)
            except Exception as e:
                db.rollback()
                raise e
        return 0
