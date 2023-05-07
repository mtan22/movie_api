from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db

import sqlalchemy 
from sqlalchemy import *

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
    with db.engine.connect() as conn:
        var = conn.execute(
            sqlalchemy.select(db.characters).where(db.characters.c.character_id == id)
        ).fetchone()
        if var:
            var = var._asdict()
            subquery1 = (
            select(
                db.conversations.c.conversation_id,
                db.conversations.c.character1_id.label('character_id'),
            )
            .where(db.conversations.c.character2_id == id)
            .cte(name='pl')
            )
            subquery2 = (
                select(
                    db.conversations.c.conversation_id,
                    db.conversations.c.character2_id.label('character_id'),
                )
                .where(db.conversations.c.character1_id == id)
                .cte(name='ml')
            )
            listb = (
                select(
                    db.characters.c.character_id,
                    db.characters.c.name.label('character'),
                    db.characters.c.gender,
                    func.count().label('number_of_lines_together')
                )
                .select_from(
                    db.lines.join(subquery1, subquery1.c.conversation_id == db.lines.c.conversation_id, isouter=True)
                    .join(subquery2, subquery2.c.conversation_id == db.lines.c.conversation_id, isouter=True)
                    .join(db.characters, db.characters.c.character_id == func.coalesce(subquery1.c.character_id, subquery2.c.character_id))
                )
                .where(db.characters.c.character_id != id)
                .group_by(db.characters.c.character_id, db.characters.c.name, db.characters.c.gender)
                .order_by(func.count().desc())
            )

            conv = conn.execute(listb).fetchall()
            conv = [c._asdict() for c in list(conv)]
            movie = (conn.execute(
                sqlalchemy.select(db.movies).where(db.movies.c.movie_id == var["movie_id"])
            ).fetchone())._asdict()
            sol = {
                "character_id": id,
                "character": var["name"],
                "movie": movie["title"],
                "gender": var["gender"],
                "top_conversations": conv,
            }
            return sol

    raise HTTPException(status_code=404, detail="character not found.")

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
    json = []
    sort_options = {
        character_sort_options.character: db.characters.c.name,
        character_sort_options.movie: db.movies.c.title,
        character_sort_options.number_of_lines: sqlalchemy.desc("number_of_lines")
    }

    if sort not in sort_options:
        assert False

    order_by = sort_options[sort]

    query = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name.label("character"),
            db.movies.c.title.label("movie"),
            sqlalchemy.func.count(db.lines.c.line_id).label("number_of_lines"),
        )
        .select_from(
            db.characters.join(db.movies, db.characters.c.movie_id == db.movies.c.movie_id)
            .join(db.lines, db.characters.c.character_id == db.lines.c.character_id)
        )
        .group_by(
            db.characters.c.character_id,
            db.characters.c.name,
            db.movies.c.title,
        )
        .order_by(order_by, db.characters.c.character_id)
        .limit(limit)
        .offset(offset)
    )
    if name != "":
        query = query.where(db.characters.c.name.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        sol = conn.execute(query)
        for i in sol:
            json.append({
                    "character_id": i.character_id,
                    "character": i.character,
                    "movie": i.movie,
                    "number_of_lines": i.number_of_lines,
                }
            )
    return json
    