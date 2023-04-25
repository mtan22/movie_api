from fastapi.testclient import TestClient

from src.api.server import app
import json

from src import database as db

client = TestClient(app)

def test_add_conversation1():
    response = client.post("/movies/0/conversations/", json={
        "character_1_id": 5,
        "character_2_id": 9,
        "lines": [{
            "character_id": 5,
            "line_text": "Do you like red apples?"
            },
            {
            "character_id": 9,
            "line_text": "No I like green apples."
            }
        ]
})
    assert response.status_code == 200


def test_add_conversation2():
    response = client.post("/movies/13/conversations/", json={
        "character_1_id": 201,
        "character_2_id": 211,
        "lines": [{
            "character_id": 201,
            "line_text": "Do you like strawberries?"
            },
            {
            "character_id": 211,
            "line_text": "No I like kiwi."
            }
        ]
})
    assert response.status_code == 200

def test_add_conversation3():
    # example of error: if movie does not exist in db
    response = client.post("/movie/2/conversations/", json={
        "character_1_id": 50,
        "character_2_id": 60,
        "lines": [{
            "character_id": 50,
            "line_text": "Hello!"
            },
            {"character_id": 60,
            "line_text": "How are you?"
            }
        ]
    })
    assert response.status_code == 404


def test_add_conversation4():
    # example of error: if both characters are identical
    response = client.post("/movie/0/conversations/", json={
        "character_1_id": 5,
        "character_2_id": 5,
        "lines": [{
            "character_id": 5,
            "line_text": "Hello!"
            },
            {"character_id": 5,
            "line_text": "How are you?"
            }
        ]
    })
    assert response.status_code == 404

def test_add_conversation5():
    # example of error: if character is not found
    response = client.post("/movie/0/conversations/", json={
        "character_1_id": 12,
        "character_2_id": 1,
        "lines": [{
            "character_id": 5,
            "line_text": "Hello!"
            },
            {"character_id": 5,
            "line_text": "How are you?"
            }
        ]
    })
    assert response.status_code == 404


def test_add_conversation6():
    # example of error: if lines don't match the characters in the conversation
    response = client.post("/movie/0/conversations/", json={
        "character_1_id": 1,
        "character_2_id": 2,
        "lines": [{
            "character_id": 1,
            "line_text": "Hello!"
            },
            {"character_id": 2,
            "line_text": "How are you?"
            }
        ]
    })
    assert response.status_code == 404

def test_add_conversation7():
    # example of error: if characters aren't in the referenced movie
    response = client.post("/movie/3/conversations/", json={
        "character_1_id": 5,
        "character_2_id": 6,
        "lines": [{
            "character_id": 1,
            "line_text": "Hello!"
            },
            {"character_id": 2,
            "line_text": "How are you?"
            }
        ]
    })
    assert response.status_code == 404