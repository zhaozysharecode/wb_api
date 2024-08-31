from fastapi import FastAPI
from fastapi import Depends, HTTPException,status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
from database import get_db
from models import User,Post,Like,Comment
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)


class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/register/")
def register(user:UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已经存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 创建新用户
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success":True, "message": "User registered successfully", "username": new_user.username}





# 秘钥和算法
SECRET_KEY = "fanmao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/login/")
def login(user:UserCreate, db: Session = Depends(get_db)):
    # 查找用户
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user or not pwd_context.verify(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 创建JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": existing_user.username}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}





oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username}
    except JWTError:
        raise credentials_exception



@app.get("/verify-token/")
def verify_token_endpoint(token: str):
    token_data = verify_token(token)
    return {"message": "Token is valid", "user": token_data["username"]}




@app.get("/posts/", response_model=List[dict])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return [{"id": post.id, "content": post.content, "owner_id": post.owner_id} for post in posts]




# @app.post("/posts/", status_code=status.HTTP_201_CREATED)
# def create_post(content: str, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
#     # 从 token_data 中获取用户名
#     username = token_data["username"]
    
#     # 获取用户信息
#     user = db.query(User).filter(User.username == username).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     # 创建新的朋友圈内容
#     new_post = Post(content=content, owner_id=user.id)
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)
    
#     return {"message": "Post created successfully", "post_id": new_post.id}



# 定义请求体的数据模型
class PostCreate(BaseModel):
    content: str

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    # 从 token_data 中获取用户名
    username = token_data["username"]
    
    # 获取用户信息
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 创建新的朋友圈内容
    new_post = Post(content=post.content, owner_id=user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return {"message": "Post created successfully", "post_id": new_post.id}





# @app.put("/posts/{post_id}", response_model=dict)
# def update_post(post_id: int, content: str, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
#     # 从 token_data 中获取用户名
#     username = token_data["username"]

#     # 查找用户和对应的帖子
#     user = db.query(User).filter(User.username == username).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
#     if post is None:
#         raise HTTPException(status_code=404, detail="Post not found or not authorized")

#     # 更新帖子内容
#     post.content = content
#     db.commit()
#     db.refresh(post)
    
#     return {"message": "Post updated successfully", "post_id": post.id, "new_content": post.content}

class PostUpdate(BaseModel):
    content: str

@app.put("/posts/{post_id}", response_model=dict)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    # 从 token_data 中获取用户名
    username = token_data["username"]

    # 查找用户和对应的帖子
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    post_record = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
    if post_record is None:
        raise HTTPException(status_code=404, detail="Post not found or not authorized")

    # 更新帖子内容
    post_record.content = post.content
    db.commit()
    db.refresh(post_record)
    
    return {"message": "Post updated successfully", "post_id": post_record.id, "new_content": post_record.content}


@app.delete("/posts/{post_id}", response_model=dict)
def delete_post(post_id: int, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    # 从 token_data 中获取用户名
    username = token_data["username"]

    # 查找用户和对应的帖子
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found or not authorized")

    # 删除帖子
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully", "post_id": post_id}


@app.post("/posts/{post_id}/like", response_model=dict)
def like_post(post_id: int, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    # 从 token_data 中获取用户名
    username = token_data["username"]

    # 获取用户信息
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 获取帖子信息
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # 检查是否已经点过赞
    like = db.query(Like).filter(Like.user_id == user.id, Like.post_id == post_id).first()
    if like:
        # 如果已经点过赞，则取消点赞
        db.delete(like)
        db.commit()
        return {"message": "Like removed", "post_id": post_id}
    else:
        # 如果没有点赞，则添加点赞
        new_like = Like(user_id=user.id, post_id=post.id)
        db.add(new_like)
        db.commit()
        return {"message": "Post liked", "post_id": post_id}


class CommentCreate(BaseModel):
    content: str
    parent_comment_id: int = None  # 可选字段，用于回复评论

@app.post("/posts/{post_id}/comments", response_model=dict)
def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    # 从 token_data 中获取用户名
    username = token_data["username"]

    # 获取用户信息
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 获取帖子信息
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # 创建新的评论或回复
    new_comment = Comment(content=comment.content, post_id=post.id, user_id=user.id, parent_comment_id=comment.parent_comment_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return {"message": "Comment created successfully", "comment_id": new_comment.id}


@app.delete("/comments/{comment_id}", response_model=dict)
def delete_comment(comment_id: int, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    # 从 token_data 中获取用户名
    username = token_data["username"]

    # 查找用户信息
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 查找评论信息
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user.id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")

    # 删除评论
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully", "comment_id": comment_id}
