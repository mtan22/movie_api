from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_get_line():
    response = client.get("/lines/68")
    assert response.status_code == 200

    with open("test/lines/68.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_line_1():
    response = client.get("/lines/697")
    assert response.status_code == 200

    with open("test/lines/697.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_lines():
    response = client.get("/lines/")
    assert response.status_code == 200

    with open("test/lines/root.json", encoding="utf-8") as f: # 
        assert response.json() == json.load(f)


# def test_sort_filter():
#     response = client.get(
#         "/lines/?text=amy&limit=50&offset=0&sort=line_text"
#     )
#     assert response.status_code == 200

#     with open(
#         "test/lines/lines-text=amy&limit=50&offset=0&sort=line_text.json",
#         encoding="utf-8",
#     ) as f:
#         assert response.json() == json.load(f)

# def test_sort_filter2():
#     response = client.get(
#         "/lines/?text=%20&limit=250&offset=42&sort=movie_title"
#     )
#     assert response.status_code == 200

#     with open(
#         "test/lines/lines-text=space&limit=250&offset=42&sort=movie_title.json",
#         encoding="utf-8",
#     ) as f:
#         assert response.json() == json.load(f)

# def test_get_conversation():
#     response = client.get("/conversations/518")
#     assert response.status_code == 200

#     with open("test/conversations/518.json", encoding="utf-8") as f:
#         assert response.json() == json.load(f)

# def test_get_conversation_1():
#     response = client.get("/conversations/753")
#     assert response.status_code == 200

#     with open("test/conversations/753.json", encoding="utf-8") as f:
#         assert response.json() == json.load(f)


def test_404():
    response = client.get("/lines/1")
    assert response.status_code == 404

