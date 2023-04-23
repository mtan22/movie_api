from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime


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
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """
    line_sort=1
    convo_char_1 = conversation.character_1_id
    convo_char_2 = conversation.character_2_id
    char1 = db.characters[convo_char_1]
    char2 = db.characters[convo_char_2]
    convo_index = 1+int(db.conversations[len(db.conversations)-1]["conversation_id"]) # getting next conversation id

    for i in conversation.lines:
        if (conversation.character_1_id != i.character_id) and (conversation.character_2_id != i.character_id):
            raise HTTPException(status_code=404, detail="lines don't match the characters involved in the conversation.")

    if char1.movie_id == char2.movie_id:
        raise HTTPException(status_code=404, detail="characters are the same.")

    if db.movies[movie_id] not in db.movies:
        raise HTTPException(status_code=404, details="movie is not found.")

    if char1 not in db.characters or char2 not in db.characters:
        raise HTTPException(status_code=404, details="character is not found.")
    
    if movie_id != char1[movie_id] or movie_id != char2[movie_id]:
        raise HTTPException(status_code=404, details="characters are not part of the referenced movie.")

    # last_index = len(db.conversations)-1

    # # add convo first so the convo id exists when conversation.lines is traversed through
    # db.conversations.append({"conversation_id": int(db.conversations[last_index]["conversation_id"]),
    # "character1_id": convo_char_1,
    # "character2_id": convo_char_2,
    # "movie_id": movie_id
    # })
    # db.upload_new_convo()

    # # add lines
    # for i in conversation.lines:
    #     char_id = i.character_id
    #     line_text = i.line_text
    #     db.lines.append({"line_id": 1+int(db.lines[len(db.lines)-1]["line_id"]), # getting next line id
    #         "character_id": char_id,
    #         "movie_id": movie_id,
    #         "conversation_id":convo_index,
    #         "line_sort": line_sort,
    #         "line_text": line_text

    #     })
    #     line_sort=line_sort+1
    # db.upload_new_lines()

    # return convo_index