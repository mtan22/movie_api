from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import sqlalchemy
from sqlalchemy import func, join, outerjoin, select

router = APIRouter()

# def get_top_convos():
#     top_conversations = (
#         db.conversations.join(db.lines, db.lines.c.conversation_id == db.conversations.c.conversation_id)
#         .join(db.characters, db.characters.c.character_id == db.lines.c.character_id))

#     top_conversations = top_conversations.with_entities(
#             func.sum(db.lines.c.num_lines).label("num_lines"),
#             db.characters.c.character_id,
#             db.characters.c.name,
#             db.characters.c.gender,
#         )

#     top_conversations = top_conversations.filter(db.conversations.c.character1_id == id).filter(db.conversations.c.character2_id == db.characters.c.character_id).group_by(db.characters.c.character_id, db.characters.c.name, db.characters.c.gender)

#     top_conversations = top_conversations.union_all(
#             db.conversations.join(db.lines, db.lines.c.conversation_id == db.conversations.c.conversation_id)
#             .join(db.characters, db.characters.c.character_id == db.lines.c.character_id)
#             .with_entities(
#                 func.sum(db.lines.c.num_lines).label("num_lines"),
#                 db.characters.c.character_id,
#                 db.characters.c.name,
#                 db.characters.c.gender,
#             )
#             .filter(db.conversations.c.character2_id == id)
#             .filter(db.conversations.c.character1_id == db.characters.c.character_id)
#             .group_by(db.characters.c.character_id, db.characters.c.name, db.characters.c.gender)).order_by(func.sum(db.lines.c.num_lines).desc()).limit(5).all()

#     return top_conversations

# @router.get("/characters/{id}", tags=["characters"])
# def get_character(id: int):
#     """
#     This endpoint returns a single character by its identifier. For each character
#     it returns:
#     * `character_id`: the internal id of the character. Can be used to query the
#       `/characters/{character_id}` endpoint.
#     * `character`: The name of the character.
#     * `movie`: The movie the character is from.
#     * `gender`: The gender of the character.
#     * `top_conversations`: A list of characters that the character has the most
#       conversations with. The characters are listed in order of the number of
#       lines together. These conversations are described below.

#     Each conversation is represented by a dictionary with the following keys:
#     * `character_id`: the internal id of the character.
#     * `character`: The name of the character.
#     * `gender`: The gender of the character.
#     * `number_of_lines_together`: The number of lines the character has with the
#       originally queried character.
#     """

#     character = db.characters.select().where(db.characters.c.character_id == id).execute()
#     character = character.first()
#     if not character:
#        raise HTTPException(422, "character not found.")

#     top_conversations = get_top_convos()

#     top_conversations_json = [
#         {
#             "character_id": character_id,
#             "character": name,
#             "gender": gender,
#             "number_of_lines_together": num_lines,
#         }
#         for num_lines, character_id, name, gender in top_conversations
#     ]

#     movie = db.movies.select().where(db.movies.c.movie_id == character.movie_id).execute()
#     movie = movie.first().title

#     json = {
#         "character_id": character.character_id,
#         "character": character.name,
#         "movie": movie,
#         "gender": character.gender,
#         "top_conversations": top_conversations_json,
#     }

#     return json




# class character_sort_options(str, Enum):
#     character = "character"
#     movie = "movie"
#     number_of_lines = "number_of_lines"


# @router.get("/characters/", tags=["characters"])
# def list_characters(
#     name: str = "",
#     limit: int = Query(50, ge=1, le=250),
#     offset: int = Query(0, ge=0),
#     sort: character_sort_options = character_sort_options.character,
# ):
#     """
#     This endpoint returns a list of characters. For each character it returns:
#     * `character_id`: the internal id of the character. Can be used to query the
#       `/characters/{character_id}` endpoint.
#     * `character`: The name of the character.
#     * `movie`: The movie the character is from.
#     * `number_of_lines`: The number of lines the character has in the movie.

#     You can filter for characters whose name contains a string by using the
#     `name` query parameter.

#     You can also sort the results by using the `sort` query parameter:
#     * `character` - Sort by character name alphabetically.
#     * `movie` - Sort by movie title alphabetically.
#     * `number_of_lines` - Sort by number of lines, highest to lowest.

#     The `limit` and `offset` query
#     parameters are used for pagination. The `limit` query parameter specifies the
#     maximum number of results to return. The `offset` query parameter specifies the
#     number of results to skip before returning results.
#     """
#     sort_columns = {
#         character_sort_options.character: db.characters.c.name,
#         character_sort_options.movie: db.movies.c.title,
#         character_sort_options.number_of_lines: sqlalchemy.desc("num_lines"),
#     }
#     order_by = sort_columns[sort]

#     query = (
#         sqlalchemy.select(
#             db.characters.c.character_id,
#             db.characters.c.name,
#             db.movies.c.title,
#             func.count(db.lines.c.line_id).label("num_lines")
#         )
#         .select_from(db.characters.outerjoin(db.movies, db.movies.c.movie_id == db.characters.c.movie_id)
#         )
#         .join(db.lines, db.characters.c.character_id == db.lines.c.character_id)
#         .group_by(db.characters.c.character_id, db.movies.c.title,)
#         .where(db.characters.c.name.ilike(f"%{name}%"))
#         .order_by(order_by, db.characters.c.character_id)
#         .limit(limit)
#         .offset(offset)
#     )

#     with db.engine.connect() as conn:
#         result = conn.execute(query)
#         json = [
#             {
#                 "character_id": row.character_id,
#                 "character": row.name,
#                 "movie": row.title,
#                 "num_lines": row.num_lines,
#             }
#             for row in result
#         ]

#     return json
   
