from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter
import re, urllib.parse

from fastapi.params import Query 
from src import database as db
import sqlalchemy
from sqlalchemy import func, join, outerjoin, select

router = APIRouter()

# @router.get("/lines/{id}", tags=["lines"])
# def get_line(id: int):
#     """
#     This endpoint returns a single character by its identifier. For each character
#     it returns:
#     * `line_id`: the internal id of the line. Can be used to query the
#       `/lines/{line_id}` endpoint.
#     * `character_id`: The internal id of the character who said the line.
#     * `character`: The name of the character who said the line.
#     * `movie_id`: The internal id of the movie that contains the line.
#     * `movie_title`: The title of the movie that contains the line.
#     * `conversation_id`: The internal id of the conversation that contains the line.
#     * `text`: The text of the line.
#     """
#     line = db.session.query(db.lines, db.characters, db.movies) \
#         .join(db.characters, db.lines.character_id == db.characters.character_id) \
#         .join(db.movies, db.characters.movie_id == db.movies.movie_id) \
#         .filter(db.lines.line_id == id).first()

#     if line is None:
#         raise HTTPException(422, "line not found.")
#     convo_id = line[0].conversation_id
#     num_total_lines = db.session.query(func.count(db.lines.line_id)) \
#         .filter(db.lines.conversation_id == convo_id).scalar()
#     num_words = len(re.findall(r'\w+', line[0].line_text))
#     num_sentences = len(re.split('[.?!]+', line[0].line_text))

#     response = {
#         "line_id": line[0].line_id,
#         "text": line[0].line_text,
#         "character": line[1].name,
#         "age": line[1].age,
#         "movie": line[2].title,
#         "line_info": {
#             "num_words": num_words,
#             "num_sentences": num_sentences,
#             "num_total_lines": num_total_lines
#         }
#     }

#     return response


# class line_sort_options(str, Enum):
#     movie_title = "movie_title"
#     line_text = "line_text"

# @router.get("/lines/", tags=["lines"])
# def list_lines(
#     text: str="",
#     limit: int = Query(50, ge=1, le=250),
#     offset: int = Query(0, ge=0),
#     sort: line_sort_options = line_sort_options.line_text,
#     ):
#     """
#     This endpoint returns a list of lines. For each line it returns:
#     * `line_id`: the internal id of the line. Can be used to query the
#       `/lines/{line_id}` endpoint.
#     * `character_id`: The internal id of the character who says the line.
#     * `character`: The character who says the line.
#     * `text`: The text of the line.
#      * `movie_title`: The movie that contains the line.

#     You can also sort the results by using the `sort` query parameter:
#     * `movie_title` - Sort by movie title alphabetically.
#     * `line_text` - Sort by text alphabetically.

#     The `limit` and `offset` query
#     parameters are used for pagination. The `limit` query parameter specifies the
#     maximum number of results to return. The `offset` query parameter specifies the
#     number of results to skip before returning results.
#     """

#     json = []

#     order_by_column = {
#         line_sort_options.character: db.characters.c.name,
#         line_sort_options.movie: db.movies.c.title,
#         line_sort_options.text: db.lines.c.line_text,
#     }[sort]
    
#     query = select(
#         db.lines.c.line_id,
#         db.lines.c.line_text,
#         db.movies.c.title,
#         db.characters.c.name
#     ).select_from(
#         join(db.lines, db.movies, db.lines.c.movie_id == db.movies.c.movie_id).join(
#             db.characters, db.lines.c.character_id == db.characters.c.character_id
#         )
#     ).limit(limit).offset(offset).order_by(order_by_column, db.lines.c.line_text)

#     if text != "":
#         query = query.filter(db.lines.c.line_text.ilike(f"%{text}%"))

#     conn = db.engine.connect()
#     sol = conn.execute(query)
#     for i in sol:
#         json.append(
#             {
#                 "line_id": i.line_id,
#                 "line_text": i.line_text,
#                 "movie": i.title,
#                 "character": i.name,
#             }
#         )
#     conn.close()
#     return json

# @router.get("/conversations/{id}", tags=["conversations"])
# def get_conversation(id: int):
#     """
#     This endpoint returns a single conversation by its identifier. For each conversation it returns:
#     * `conversation_id`: the internal id of the conversation.
#     * `character`: The name of the character that said the line.
#     * `movie_id`: The internal id of the movie that contains the line.
#     * `movie_title`: The title of the movie the line is from.
#     * `conversation`: The text of the conversation.
#      Each conversation is represented by a dictionary with the following keys:
#     * `character_id`: the internal id of the character.
#     * `character`: The name of the character.
#     * `line' : The text of the line.
#     """
#     lines = []
#     json = []
#     query = select([
#         db.conversations.c.conversation_id,
#         db.characters.c.name.label('character'),
#         db.movies.c.movie_id,
#         db.movies.c.title.label('movie_title'),
#         db.conversations.c.conversation
#     ]).select_from(
#         join(db.conversations, db.lines, db.conversations.c.conversation_id == db.lines.c.conversation_id)
#         .join(db.characters, db.lines.c.character_id == db.characters.c.character_id)
#         .join(db.movies, db.lines.c.movie_id == db.movies.c.movie_id)
#     ).where(db.conversations.c.conversation_id == id)

#     with db.engine.connect() as conn:
#         result = conn.execute(query).fetchone()
#         if result is None:
#             raise HTTPException(422, "no conversation found.")
#         conversation_id, character, movie_id, movie_title, conversation = result
#         line_query = select([
#             db.characters.c.character_id,
#             db.characters.c.name.label('character'),
#             db.lines.c.line_text.label('line')
#         ]).select_from(
#             join(db.lines, db.characters, db.lines.c.character_id == db.characters.c.character_id)
#         ).where(db.lines.c.conversation_id == conversation_id).order_by(db.lines.c.line_number)

#         for line in conn.execute(line_query):
#             lines.append({
#                 "character_id": line.character_id,
#                 "character": line.character,
#                 "line": line.line
#             })
    
#         json.append({
#             "conversation_id": conversation_id,
#             "character": character,
#             "movie_id": movie_id,
#             "movie_title": movie_title,
#             "conversation": conversation,
#             "lines": lines
#         })

#         return json

