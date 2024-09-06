from fastapi import FastAPI
from models import Base
from database import engine, Base
from routers import auth, blogs, users

app = FastAPI()


Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(blogs.router)
app.include_router(users.router)