from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_add_conversation1():
    obj = {
        "character_1_id": 50,
        "character_2_id": 60,
        "lines": [{
            "character_id": 50,
            "line_text": "My dress is blue!"
            },
            {"character_id": 60,
            "line_text": "My shirt is orange!"
            }
        ]
    }
    response = client.post("/movie/3/conversations/", json=obj)
    assert response.status_code == 200

def test_add_conversation2():
    obj = {
        "character_1_id": 612,
        "character_2_id": 623,
        "lines": [{
            "character_id": 612,
            "line_text": "Do you like strawberries?"
            },
            {"character_id": 623,
            "line_text": "No. I like kiwi."
            }
        ]
    }
    response = client.post("/movie/39/conversations/", json=obj)
    assert response.status_code == 200

def test_add_conversation3():
    # example of error: if movie does not exist in db
    obj = {
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
    }
    response = client.post("/movie/2/conversations/", json=obj)
    assert response.status_code == 404