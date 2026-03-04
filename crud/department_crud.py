from pyodbc import Connection


class DepartmentCRUD:
    @staticmethod
    def get_all(db: Connection):
        # Sử dụng with để tự động đóng cursor, tránh treo DB
        with db.cursor() as cursor:
            cursor.execute("SELECT DeptID, DeptName FROM Departments ORDER BY DeptName")
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def check_exists_name(db: Connection, name: str, exclude_id: int = None):
        with db.cursor() as cursor:
            if exclude_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM Departments WHERE DeptName = ? AND DeptID != ?",
                    (name, exclude_id),
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM Departments WHERE DeptName = ?", (name,)
                )
            return cursor.fetchone()[0] > 0

    @staticmethod
    def check_employee_relation(db: Connection, dept_id: int):
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM Employees WHERE IdDepartment = ?", (dept_id,)
            )
            row = cursor.fetchone()
            # Lấy phần tử đầu tiên của Tuple (vị trí 0)
            return row[0] if row else 0

    @staticmethod
    def insert(db: Connection, name: str):
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO Departments (DeptName) VALUES (?)", (name,))

    @staticmethod
    def update(db: Connection, dept_id: int, name: str):
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE Departments SET DeptName=? WHERE DeptID=?", (name, dept_id)
            )

    @staticmethod
    def delete(db: Connection, dept_id: int):
        cursor = db.cursor()
        cursor.execute("DELETE FROM Departments WHERE DeptID = ?", (dept_id,))
