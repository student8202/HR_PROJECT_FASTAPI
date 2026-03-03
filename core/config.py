import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SMILE HR PROFESSIONAL"
    SECRET_KEY: str = "AnhMinh167TruongDinh_Secret_Key_2024"
    
    # Cấu hình SQL Server
    DB_DRIVER: str = "{ODBC Driver 17 for SQL Server}"
    DB_SERVER: str = "localhost"
    DB_NAME: str = "SMILE_HR"
    DB_USER: str = "smile"
    DB_PASSWORD: str = "AnhMinh167TruongDinh"

    @property
    def connection_string(self) -> str:
        # Thêm TrustServerCertificate=yes nếu bạn dùng SQL Server bản mới bị lỗi SSL
        return (
            f"DRIVER={self.DB_DRIVER};"
            f"SERVER={self.DB_SERVER};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD};"
            "Trusted_Connection=no;" 
        )

    class Config:
        case_sensitive = True

settings = Settings()
