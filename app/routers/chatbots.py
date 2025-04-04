from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, models
from ..dependencies import oauth2_scheme
from ..database import get_db

router = APIRouter(
    prefix="/chatbots",
    tags=["chatbots"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.Chatbot])
def get_chatbots(limit: int = 10, offset: int = 0, db = Depends(get_db), current_user=Depends(oauth2_scheme)):
    return db.query(models.Chatbot).offset(offset).limit(limit).all()

@router.get("/{chatbot_id}", response_model=schemas.Chatbot)
def get_chatbot(chatbot_id: int, db = Depends(get_db), current_user=Depends(oauth2_scheme)):
    chatbot = db.query(models.Chatbot).filter(schemas.Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    return chatbot

@router.post("/", response_model=schemas.Chatbot)
def create_chatbot(chatbot: schemas.Chatbot, db = Depends(get_db), current_user=Depends(oauth2_scheme)):
    print("Creating chatbot...")
    new_chatbot = models.Chatbot(**chatbot.model_dump())
    db.add(new_chatbot)
    db.commit()
    db.refresh(new_chatbot)
    return new_chatbot

@router.patch("/{chatbot_id}", response_model=schemas.Chatbot)
def update_chatbot(chatbot_id: int, chatbot: schemas.ChatbotUpdate, db = Depends(get_db), current_user=Depends(oauth2_scheme)):
    db_chatbot = db.query(models.Chatbot).filter(schemas.Chatbot.id == chatbot_id).first()
    if not db_chatbot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    for key, value in chatbot.model_dump(exclude_unset=True).items():
        setattr(db_chatbot, key, value)
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot