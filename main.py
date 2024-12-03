from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import List
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI()

DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    genre = Column(String, index=True)
    year = Column(Integer)
    description = Column(String)

Base.metadata.create_all(bind=engine)

class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    year: int
    description: str

class BookResponse(BookCreate):
    id: UUID


@app.post("/books", response_model=BookResponse)
def create_book(book: BookCreate):
    db = SessionLocal()
    db_book = Book(id=str(uuid4()), title=book.title, author=str(book.author), genre=str(book.genre), year=book.year, description=book.description)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books", response_model=List[BookResponse])
def read_books():
    db = SessionLocal()
    books = db.query(Book).all()
    return books

@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: UUID):
    db = SessionLocal()
    book = db.query(Book).filter(Book.id == str(book_id)).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: UUID, book: BookCreate):
    db = SessionLocal()
    db_book = db.query(Book).filter(Book.id == str(book_id)).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.title = book.title
    db_book.author = str(book.author)
    db_book.genre = str(book.genre)
    db_book.year = book.year
    db_book.description = book.description
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}")
def delete_book(book_id: UUID):
    db = SessionLocal()
    db_book = db.query(Book).filter(Book.id == str(book_id)).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()

    return {"message": "Book successfully deleted"}
