from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter
from fastapi.params import Query 
from src import database as db
import sqlalchemy
from sqlalchemy import *

router = APIRouter()

@router.get("/lines/{id}", tags=["lines"])
def get_line(id: int):
    """
    This endpoint returns a single line by its identifier. For each line
    it returns:
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `character_id`: The internal id of the character who said the line.
    * `character`: The name of the character who said the line.
    * `movie_id`: The internal id of the movie that contains the line.
    * `movie_title`: The title of the movie that contains the line.
    * `conversation_id`: The internal id of the conversation that contains the line.
    * `text`: The text of the line.
    """
    with db.engine.connect() as conn:
        var = select(
            db.lines.c.line_id,
            db.lines.c.character_id,
            db.characters.c.name,
            db.movies.c.movie_id,
            db.movies.c.title,
            db.lines.c.line_text,
            db.lines.c.conversation_id
        ).select_from(
            join(
                join(db.lines, db.characters, db.lines.c.character_id == db.characters.c.character_id),
                db.movies, db.lines.c.movie_id == db.movies.c.movie_id
            )
        ).where(
            db.lines.c.line_id == id
        )
        var = conn.execute(var).fetchall()

        if var:
            line_dict = [row._asdict() for row in var]
            result = {
                "line_id": line_dict[0]["line_id"],
                "character_id": line_dict[0]["character_id"],
                "character": line_dict[0]["name"],
                "movie_id": line_dict[0]["movie_id"],
                "movie": line_dict[0]["title"],
                "conversation_id": line_dict[0]["conversation_id"],
                "text": line_dict[0]["line_text"],
            }

            return result

    raise HTTPException(status_code=404, detail="line not found.")


class line_sort_options(str, Enum):
    movie_title = "movie_title"
    line_text = "line_text"

@router.get("/lines/", tags=["lines"])
def list_lines(
    text: str="",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: line_sort_options = line_sort_options.line_text,
    ):
    """
    This endpoint returns a list of lines. For each line it returns:
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `character_id`: The internal id of the character who says the line.
    * `character`: The character who says the line.
    * `text`: The text of the line.
     * `movie_title`: The movie that contains the line.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `line_text` - Sort by text alphabetically.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    if sort is line_sort_options.movie_title:
        order_by = db.movies.c.title
    elif sort is line_sort_options.line_text:
        order_by = db.lines.c.line_text
    else:
        assert False

    with db.engine.connect() as conn:
        query = select(
            db.lines.c.line_id,
            db.characters.c.name.label("character"),
            db.movies.c.title.label("movie"),
            db.lines.c.conversation_id,
            db.lines.c.line_text,
        ).select_from(
            join(
                join(db.lines, db.characters, db.lines.c.character_id == db.characters.c.character_id),
                db.movies, db.lines.c.movie_id == db.movies.c.movie_id
            )
        ).where(
            db.characters.c.name.ilike(f"%{text}%")
        ).limit(limit).offset(offset).order_by(order_by, db.lines.c.line_text)
        
        sol = conn.execute(query).fetchall()

        if sol:
            sol = [i._asdict() for i in sol]
            return sol
        
    raise HTTPException(status_code=404, detail="lines not found.")

@router.get("/conversations/{id}", tags=["conversations"])
def get_conversation(id: int):
    """
    This endpoint returns a single conversation by its identifier. For each conversation it returns:
    * `conversation_id`: the internal id of the conversation.
    * `character_1`: The name of the character 1 in the conversation.
    * `character_2`: The name of the character 2 in the conversation.
    * `movie_title`: The title of the movie the line is from.
    * `lines`: The text of the conversation.
    Every line in lines is represented by a dictionary consisting of:
       * `line_id`: the internal id of the line.
       * `character`: the character who said the line.
       * `line_text`: the text of the line.
    """
    with db.engine.connect() as conn:
        query = f"""
        SELECT convos.conversation_id convo_id, c1.name character_1, c2.name character_2, m.title movie
        FROM conversations as convos
        JOIN movies as m ON m.movie_id = convos.movie_id
        JOIN characters as c1 ON c1.character_id = convos.character1_id
        JOIN characters as c2 ON c2.character_id = convos.character2_id
        WHERE {id} = convos.conversation_id
        """

        convo = conn.execute(sqlalchemy.text(query),).fetchone()._asdict()
        if convo:
            query = select(
                db.lines.c.line_id,
                db.characters.c.name.label("character"),
                db.lines.c.line_text
            ).select_from(
                join(
                    db.lines,
                    db.characters,
                    db.lines.c.character_id == db.characters.c.character_id
                )
            ).where(
                db.lines.c.conversation_id == id
            )
            convo["lines"] = [l._asdict() for l in conn.execute(query).fetchall()]
            return convo

    raise HTTPException(status_code=404, detail="line not found.")
