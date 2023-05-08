from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import Session

# FastAPI is inferring what the request body should look like
# based on the following two classes.


class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()

@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson, db: Session):
    with db.engine.begin() as conn:
        vars = conn.execute(sqlalchemy.select(db.characters.c.character_id).where(db.characters.c.movie_id == movie_id)
        )
        vars = vars.fetchall()
        id_list = {c.character_id for c in vars}
        if not set([conversation.character_1_id, conversation.character_2_id]).issubset(id_list):
            raise HTTPException(status_code=400, detail="character not in movie")
        if conversation.character_1_id == conversation.character_2_id:
            raise HTTPException(status_code=400, detail="characters are the same")
        convo_id = conn.execute(
            sqlalchemy.select(sqlalchemy.func.max(db.conversations.c.conversation_id))
        ).scalar()+ 1
        conn.execute(
            db.conversations.insert().values(
                conversation_id=convo_id,
                character1_id=conversation.character_1_id,
                character2_id=conversation.character_2_id,
                movie_id=movie_id,
            )
        )
        line_id = conn.execute(
            sqlalchemy.select(sqlalchemy.func.max(db.lines.c.line_id))
        ).scalar()+1
        lista = [
            {
                "line_id": line_id+i,
                "character_id": line.character_id,
                "movie_id": movie_id,
                "conversation_id": convo_id,
                "line_sort": i,
                "line_text": line.line_text
            }
            for i, line in enumerate(conversation.lines)
        ]
        
        conn.execute(db.lines.insert(), lista)
        conn.commit()
        json = {'id': convo_id}

    return json