from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import sqlalchemy
from sqlalchemy import func, join, outerjoin, select

router = APIRouter()

@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """
    query = (
        db.characters.join(db.movies)
        .join(
            db.conversations,
            sqlalchemy.or_(
                db.conversations.c.character1_id == id,
                db.conversations.c.character2_id == id,
            ),
        )
        .join(db.lines, db.lines.c.conversation_id == db.conversations.c.conversation_id)
        .join(db.characters.alias("c2"), db.lines.c.character_id != id)
        .select(
            db.characters.c.character_id,
            db.characters.c.name.label("character"),
            db.movies.c.title.label("movie"),
            db.characters.c.gender,
            sqlalchemy.func.count(db.lines.c.line_id).label("number_of_lines_together"),
            db.characters.c.character_id.label("c2_character_id"),
            db.characters.alias("c2").c.name.label("c2_character"),
            db.characters.alias("c2").c.gender.label("c2_gender"),
        )
        .where(db.characters.c.character_id == id)
        .group_by(
            db.characters.c.character_id,
            db.movies.c.title,
            db.characters.c.gender,
            db.characters.c.name,
            db.characters.alias("c2").c.name,
            db.characters.alias("c2").c.gender,
            db.characters.alias("c2").c.character_id,
        )
    )

    with db.engine.connect() as conn:
        results = conn.execute(query)

        json = []
        for i in results:
            json.append(i)

        if not json:
            raise HTTPException(status_code=404, detail="character not found.")

        character = {
            "character_id": json[0]["character_id"],
            "character": json[0]["character"],
            "movie": json[0]["movie"],
            "gender": json[0]["gender"],
        }

        top_conversations = []
        for i in json:
            if i["c2_character_id"] != id:
                top_conversations.append(
                    {
                        "character_id": i["c2_character_id"],
                        "character": i["c2_character"],
                        "gender": i["c2_gender"],
                        "number_of_lines_together": i["number_of_lines_together"],
                    }
                )

        character["top_conversations"] = top_conversations

        return character

class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    sort_columns = {
        character_sort_options.character: db.characters.c.name,
        character_sort_options.movie: db.movies.c.title,
        character_sort_options.number_of_lines: sqlalchemy.func.count(db.lines.c.line_text).desc(),
    }
    order_by = sort_columns[sort]

    query = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name.label("character"),
            db.movies.c.title.label("movie"),
            sqlalchemy.func.count(db.lines.c.line_text).label("number_of_lines"),
        )
        .select_from(db.characters.join(db.movies).outerjoin(db.lines))
        .where(db.characters.c.name.ilike(f"%{name}%"))
        .group_by(db.characters.c.character_id, db.movies.c.title)
        .order_by(sort_columns[sort])
        .limit(limit)
        .offset(offset)
    )

    with db.engine.connect() as conn:
        result = conn.execute(query)
        json = [
            {
                "character_id": row.character_id,
                "character": row.name,
                "movie": row.title,
                "num_lines": row.num_lines,
            }
            for row in result
        ]

    return json
   
