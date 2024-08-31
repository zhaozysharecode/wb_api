from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database import SessionLocal

from models import Base, User

# 配置数据库连接
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://fastapi:ABCfastapi123@rm-bp160xxxz5no45g22eo.mysql.rds.aliyuncs.com/mydb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建数据库表
Base.metadata.create_all(bind=engine)

print("Database and tables created successfully.")

# 测试数据库连接
def test_db():
    db: Session = SessionLocal()
    try:
        # 测试数据库是否可以正常访问
        users = db.query(User).all()
        print("Successfully connected to the database.")
        print("Number of users in the database:", len(users))
    finally:
        db.close()

test_db()



