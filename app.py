# simple hello world with fast api

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return "Hello Automated World"
