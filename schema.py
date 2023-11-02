from typing import List
from sqlalchemy import String, ForeignKey, Text, Boolean, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    blogs: Mapped[List["Blog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    likes: Mapped[List["Like"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"
    
class Blog(Base):
    __tablename__ = "blog"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    content: Mapped[str] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="blogs")

    likes: Mapped[List["Like"]] = relationship(back_populates="blog", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship(back_populates="blog", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Blog(id={self.id!r}, content={self.content!r})"

class Like(Base):
    __tablename__ = "like"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    blog_id: Mapped[int] = mapped_column(ForeignKey("blog.id"))

    user: Mapped["User"] = relationship(back_populates="likes")
    blog: Mapped["Blog"] = relationship(back_populates="likes")

    like = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"Like(id={self.id!r}, blog_id={self.blog_id!r}, user_id={self.user_id!r}, like={self.like!r})"

class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    blog_id: Mapped[int] = mapped_column(ForeignKey("blog.id"))

    user: Mapped["User"] = relationship(back_populates="comments")
    blog: Mapped["Blog"] = relationship(back_populates="comments")

    content: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"Like(id={self.id!r}, blog_id={self.blog_id!r}, user_id={self.user_id!r}, content={self.content!r})"

if __name__ == "__main__":
    engine = create_engine("mysql+pymysql://chan:Diy.2002@localhost/blog", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session: 
        user = User(
            name="test",
        )
        print(user)

        blog = Blog(content="test content", user=user)
        print(blog)

        comment = Comment(content="test comment", user=user, blog=blog)
        like = Like(like=True, user=user, blog=blog)

        session.add_all([user, blog, comment, like])
        session.commit()
        print(user)
