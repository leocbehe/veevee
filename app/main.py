from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from .routers import users, chatbots, documents

app = FastAPI(
    title="VeeVee",
    description= """
        Chatbot VeeVee
        """
)

app.include_router(users.router)

@app.get("/")
def root():
    return {"Success": "The application is up and running!"}
