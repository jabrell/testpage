# simple hello world with fast api

from fastapi import FastAPI

from app.routers import user_router

app = FastAPI()

# include routes
app.include_router(user_router)


@app.get("/")
def read_root():
    return "Hello Automated World"
