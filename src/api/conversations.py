from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import select, and_, or_
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

def add_conversation(movie_id: int, conversation: ConversationJson, db: Session):
    if conversation.character_1_id == conversation.character_2_id:
        raise HTTPException(status_code=404, detail="characters are not unique.")
    movie = db.query(db.movies).filter_by(movie_id=movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="movie not found.")
    characters = db.query(db.characters).filter(
        and_(db.characters.c.movie_id == movie_id,
             or_(db.characters.c.character_id == conversation.character_1_id,
                 db.characters.c.character_id == conversation.character_2_id))).all()
    if len(characters) != 2:
        raise HTTPException(status_code=404, detail="character not found.")
    if characters[0].movie_id != characters[1].movie_id:
        raise HTTPException(status_code=404, detail="character and movie are not referenced together.")

    line_id = db.query(db.lines.c.line_id).order_by(db.lines.c.line_id.desc()).first()
    conv_id = db.query(db.conversations.c.conversation_id).order_by(
        db.conversations.c.conversation_id.desc()).first()
    ids = []
    if line_id:
        ids.append(line_id[0] + 1)
    else:
        ids.append(1)
    if conv_id:
        ids.append(conv_id[0] + 1)
    else:
        ids.append(1)
    conversation_db = db.conversations(
        conversation_id=conv_id,
        character1_id=conversation.character_1_id,
        character2_id=conversation.character_2_id,
        movie_id=movie_id
    )
    db.add(conversation_db)

    for idx, line in enumerate(conversation.lines):
        if line.character_id not in (conversation.character_1_id, conversation.character_2_id):
            raise HTTPException(status_code=404, detail="character not in conversation.")
        line_db = db.lines(
            line_id=line_id,
            character_id=line.character_id,
            movie_id=movie_id,
            conversation_id=conv_id,
            line_sort=idx + 1,
            line_text=line.line_text
        )
        db.add(line_db)
        line_id += 1

    db.commit()

    return conv_id