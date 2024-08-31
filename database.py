from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 配置数据库连接字符串
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://fastapi:ABCfastapi123@rm-bp160xxxz5no45g22eo.mysql.rds.aliyuncs.com/mydb"

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建一个会话工厂，用于生成数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础类，用于模型继承
Base = declarative_base()

# 依赖项，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
