from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# 创建一个基础类，用于之后的模型继承
Base = declarative_base()

# 定义User模型
class User(Base):
    __tablename__ = "users"  # 数据库中表的名称

    id = Column(Integer, primary_key=True, index=True)  # 用户的唯一标识符
    username = Column(String(50), unique=True, index=True)  # 用户名，必须唯一
    hashed_password = Column(String(255))  # 存储加密后的密码
    
    posts = relationship("Post", back_populates="owner")  # 用户与其发布的帖子之间的关系
    likes = relationship("Like", back_populates="user") # 用户与其点赞的帖子之间的关系
    comments = relationship("Comment", back_populates="user") # 用户与其评论的帖子之间的关系



# 继续使用之前的 Base
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), index=True)  # 朋友圈内容
    owner_id = Column(Integer, ForeignKey("users.id"))  # 发布此内容的用户ID

    owner = relationship("User", back_populates="posts") # 帖子与用户之间的关系
    likes = relationship("Like", back_populates="post") # 帖子与点赞之间的关系
    comments = relationship("Comment", back_populates="post") # 帖子与评论之间的关系



class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), index=True)  # 评论内容
    post_id = Column(Integer, ForeignKey("posts.id"))  # 被评论的帖子ID
    user_id = Column(Integer, ForeignKey("users.id"))  # 评论的用户ID
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # 回复的父评论ID

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])