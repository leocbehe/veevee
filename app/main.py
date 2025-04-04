from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from .routers import users, auth, chatbots, conversations

app = FastAPI(
    title="VeeVee",
    description= """
        Chatbot VeeVee
        """
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(chatbots.router)
app.include_router(conversations.router)

@app.get("/")
def root():
    return {"Success": "The application is up and running!"}