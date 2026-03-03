from fastapi import APIRouter, Depends, HTTPException
from pyodbc import Connection
from database import get_db
from controllers.department_ctl import DepartmentController
from schemas.department import DepartmentSaveRequest

router = APIRouter(tags=["Phòng ban"])

@router.get("/api/all")
async def get_departments(db: Connection = Depends(get_db)):
    return DepartmentController.get_all(db)

@router.post("/api/save")
async def save_department(data: DepartmentSaveRequest, db: Connection = Depends(get_db)):
    success, message = DepartmentController.save(db, data)
    if not success:
        return {"status": "error", "message": message}
    return {"status": "success", "message": message}

@router.delete("/api/delete/{dept_id}")
async def delete_department(dept_id: int, db: Connection = Depends(get_db)):
    success, message = DepartmentController.delete(db, dept_id)
    if not success:
        return {"status": "error", "message": message}
    return {"status": "success", "message": message}
