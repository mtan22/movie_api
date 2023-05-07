from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
import sqlalchemy
from sqlalchemy import func, join, outerjoin, select, desc
from fastapi.params import Query

router = APIRouter()

@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: int):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """
    json = None
    chars = []

    with db.engine.connect() as conn:
        sub_query = (
            sqlalchemy.select(
                db.movies.c.movie_id,
                db.movies.c.title,
            )
            .where(db.movies.c.movie_id == movie_id)
        )
        sol = conn.execute(sub_query)

        stmt = (
        sqlalchemy.select(
            db.characters.c.character_id, 
            db.characters.c.name, 
            func.count(db.lines.c.line_id).label("num_lines"),
        )
        .select_from(
            db.characters.join(db.lines, db.characters.c.character_id == db.lines.c.character_id)
        )
        .where(db.characters.c.movie_id == movie_id)
        .group_by(db.characters.c.character_id, db.characters.c.name)
        .order_by(sqlalchemy.desc("num_lines"))
        .limit(5)
        )
        res = conn.execute(stmt)
        for i in res:
            chars.append(
                {
                    "character_id": i.character_id,
                    "character": i.name,
                    "num_lines": i.num_lines,
                }
            )
        for i in sol:
            json = {
                "movie_id": i.movie_id,
                "title": i.title,
                "top_characters": chars,
            }

    if json is None:
        raise HTTPException(status_code=404, detail="movie not found.")
    return json

class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    json=[]

    order_by_column = {
        movie_sort_options.movie_title: db.movies.c.title,
        movie_sort_options.year: db.movies.c.year,
        movie_sort_options.rating: sqlalchemy.desc(db.movies.c.imdb_rating),
    }[sort]

    query = (
        sqlalchemy.select(
            db.movies.c.movie_id,
            db.movies.c.title,
            db.movies.c.year,
            db.movies.c.imdb_rating,
            db.movies.c.imdb_votes,
        )
        .limit(limit)
        .offset(offset)
        .order_by(order_by_column, db.movies.c.movie_id)
    )
    if name != "":
        query = query.filter(db.movies.c.title.ilike(f"%{name}%"))

    conn = db.engine.connect()
    sol = conn.execute(query)
    for i in sol:
        json.append(
            {
                "movie_id": i.movie_id,
                "movie_title": i.title,
                "year": i.year,
                "imdb_rating": i.imdb_rating,
                "imdb_votes": i.imdb_votes,
            }
        )

    conn.close()

    return json