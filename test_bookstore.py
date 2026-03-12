
"""
Exam 2 - Bookstore API Integration Tests
==========================================
Write your tests below. Each section (Part B and Part D) is marked.
Follow the instructions in each part carefully.


Run your tests with:
    pytest test_bookstore.py -v


Run with coverage:
    pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
"""


import pytest
from bookstore_app import app




# ============================================================
# FIXTURE: Test client with isolated database (provided)
# ============================================================


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client with a temporary database."""
    db_path = str(tmp_path / "test_bookstore.db")
    monkeypatch.setattr("bookstore_db.DB_NAME", db_path)


    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ============================================================
# HELPER: Create a book (provided for convenience)
# ============================================================

def create_sample_book(client, title="The Great Gatsby", author="F. Scott Fitzgerald", price=12.99):
    """Helper to create a book and return the response JSON."""
    response = client.post("/books", json={
        "title": title,
        "author": author,
        "price": price,
    })
    return response

# ============================================================
# PART B - Integration Tests (20 marks)
# Write at least 14 tests covering ALL of the following:
#
# POST /books:
#   - Create a valid book (check 201 and response body)
def test_create_valid_book(client):
    response = create_sample_book(client)
    assert response.status_code == 201
    data = response.get_json()
    assert data["book"]["title"] == "The Great Gatsby"
    assert data["book"]["author"] == "F. Scott Fitzgerald"

#   - Create with missing title (check 400)
def test_create_book_notitle(client):
    response = client.post("/books", json={
        "author": "kale madden",
        "price": 12.50
    })
    assert response.status_code==400


#   - Create with empty author (check 400)
def test_create_book_noauthor(client):
    response = client.post("/books", json={"title": "Cinderella","author": "", "price": 12.50})
    assert response.status_code==400

#   - Create with invalid price (check 400)
def test_create_book_invalidprice(client):
    response = client.post("/books", json={
        "title": "Cinderella",
        "author": "kale madden",
        "price": -10000
    })

    assert response.status_code == 400
#
# GET /books:
#   - List books when empty (check 200, empty list)
def test_empty_list_books(client):
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert data["books"] == []

#   - List books after adding 2+ books (check count)
def test_list_twobooks(client):
    create_sample_book(client)
    create_sample_book(client)
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["books"]) == 2
#
# GET /books/<id>:
#   - Get an existing book (check 200)
def test_getbook(client):
    response = create_sample_book(client)
    book_id = response.get_json()["book"]["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["book"]["title"] == "The Great Gatsby"
    assert data["book"]["id"] == book_id

#   - Get a non-existing book (check 404)
def test_get_nonexisting_book(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"].lower()
#
# PUT /books/<id>:
#   - Update a book's title (check 200 and new value)
def test_update_title(client):
    response = create_sample_book(client)
    book_id = response.get_json()["book"]["id"]
    response = client.put(f"/books/{book_id}", json={"title": "Cinderella"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["book"]["title"] == "Cinderella"

#   - Update with invalid price (check 400)
def test_update_invalidprice(client):
    response = create_sample_book(client)
    book_id = response.get_json()["book"]["id"]
    response = client.put(f"/books/{book_id}", json={ "price": -1000 })
    assert response.status_code == 400
    assert "positive" in response.get_json()["error"].lower()

#   - Update a non-existing book (check 404)
def test_update_nonexisting_book(client):
    response = client.put("/books/88889", json={"title": "lorem"})
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"].lower()

#
# DELETE /books/<id>:
#   - Delete an existing book (check 200, then confirm 404)
def test_delete_book(client):
    resp = create_sample_book(client)
    book_id = resp.get_json()["book"]["id"]
    del_response = client.delete(f"/books/{book_id}")
    assert del_response.status_code == 200
    # Confirm it's gone
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404

#   - Delete a non-existing book (check 404)
def test_delete_non_existing_book(client):
    response = client.delete("/books/99999")
    assert response.status_code == 404
#
# Full workflow:
#   - Create -> Read -> Update -> Read again -> Delete -> Confirm gone
def test_fullworkflow(client):

    # Create a book
    response = create_sample_book(client)
    assert response.status_code == 201
    book_id = response.get_json()["book"]["id"]

    # Read a book
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200

    # Update a title 
    response = client.put(f"/books/{book_id}", json={"title": "cinderella"})
    assert response.status_code == 200

    # Read the titlke after update
    response = client.get(f"/books/{book_id}")
    assert response.get_json()["book"]["title"] == "cinderella"

    # Delete 
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200

    # Confirm gone
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404
# ============================================================


# TODO: Write your Part B tests here


# ============================================================
# PART D - Coverage (5 marks)
# Run: pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
# You must achieve 85%+ coverage across both files.
# If lines are missed, add more tests above to cover them.
# ============================================================




# ============================================================
# BONUS (5 extra marks)
# 1. Add a search endpoint to bookstore_app.py:
#    GET /books/search?q=<query>
#    - Uses search_books() from bookstore_db.py
#    - Returns {"books": [...]} with status 200
#    - Returns {"error": "Search query is required"} with 400 if q is missing
#
# 2. Write 3 integration tests for the search endpoint:
#    - Search by title (partial match)
#    - Search by author (partial match)
#    - Search with no results (empty list)
# ============================================================


# TODO: Write your bonus tests here (optional)
