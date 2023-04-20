from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db

router = APIRouter()

@router.get("/lines/{id}", tags=["lines"])
def get_line(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
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

    line = db.lines.get(id)

    if line:
        character = db.characters.get(line.c_id)
        result = {
            "line_id": id,
            "character_id": line.c_id,
            "character": character.name,
            "movie_id": line.movie_id,
            "movie_title": db.movies[line.movie_id].title,
            "conversation_id": line.conv_id,
            "line_text": line.line_text
        }
        return result
    else:
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
     
    if text:
        def filter_fn(line):
            return (text in line.line_text)
    else:
        def filter_fn(line):
            return True
    lista = list(filter(filter_fn, db.lines.values()))
    
    if sort == line_sort_options.movie_title:
        lista.sort(key=lambda i: db.movies[i.movie_id].title)
    elif sort == line_sort_options.line_text:
        lista = [i for i in lista if i.line_text]
        lista.sort(key=lambda i: i.line_text)
    
    json = ({
            "line_id": i.id,
            "character_id": i.c_id,
            "character": db.characters[i.c_id].name,
            "text": i.line_text,
            "movie_title": db.movies[i.movie_id].title,
            }
            for i in lista[offset:offset + limit])
    return json


@router.get("/conversations/{id}", tags=["conversations"])
def get_conversation(id: int):
    """
    This endpoint returns a single conversation by its identifier. For each conversation it returns:
    * `conversation_id`: the internal id of the conversation.
    * `character`: The name of the character that said the line.
    * `movie_id`: The internal id of the movie that contains the line.
    * `movie_title`: The title of the movie the line is from.
    * `conversation`: The text of the conversation.
     Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `line' : The text of the line.
    """

    c = db.conversations.get(id)
    if c:
        movie = db.movies.get(c.movie_id)
        result = {
            "conversation_id": id,
            "movie_id": c.movie_id,
            "movie_title": movie.title,
            "conversation": ( 
                {"character_id": i.c_id,
                "character": db.characters.get(i.c_id).name,
                "line": i.line_text} 
                for i in db.lines.values() if id == i.id
            )
        }
        return result
    raise HTTPException(status_code=404, detail="conversation not found.")

