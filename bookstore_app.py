from flask import Flask, request, jsonify
from bookstore_db import (
    init_db, add_book, get_all_books, get_book,
    update_book, delete_book, search_books,
)


app = Flask(__name__)

@app.before_request
def setup():
    init_db()


# ----- ENDPOINT 1: List all books (DONE) -----
@app.route("/books", methods=["GET"])
def list_books():
    books = get_all_books()
    return jsonify({"books": books}), 200


# ----- ENDPOINT 2: Create a new book (DONE) -----
@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()
    if not data or "title" not in data or "author" not in data or "price" not in data:
        return jsonify({"error": "title, author, and price are required"}), 400
    try:
        book_id = add_book(data["title"], data["author"], data["price"])
        book = get_book(book_id)
        return jsonify({"book": book}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/books/search", methods=["GET"])
def search_books_ep():
    query = request.args.get("q", "").strip()
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    results = search_books(query)
    return jsonify({"books": results}), 200

# ----- ENDPOINT 3: Get a single book by ID (TODO) -----
# Route: GET /books/<int:book_id>
@app.route("/books/<int:book_id>", methods=["GET"])   
def get_book_by_id(book_id):
    book = get_book(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"book": book}), 200


# ----- ENDPOINT 4: Update a book (TODO) -----
# Route: PUT /books/<int:book_id> done
# - Accept JSON body with optional fields: title, author, price done
# - Return the updated book as JSON with status 200 done
# - Return 404 if book not found done
# - Return 400 if validation fails (e.g. price <= 0) done

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book_byid(book_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        update_book(book_id,title=data.get("title"),author=data.get("author"),price=data.get("price"),)
        updated_book = get_book(book_id)
        return jsonify({"book": updated_book}), 200
    except ValueError as error:
        error_message = str(error)
        if 'not found' in error_message.lower():
            return jsonify({"error": error_message}), 404
        else:
            return jsonify({"error": error_message}), 400



# ----- ENDPOINT 5: Delete a book (TODO) -----
# Route: DELETE /books/<int:book_id>
# - Return {"message": "Book deleted"} with status 200
# - Return {"error": "..."} with status 404 if not found

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_single_book(book_id):
    try:
        delete_book(book_id)
        return jsonify({"message": "Book deleted"}), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
    





if __name__ == "__main__":
    app.run(debug=True)
