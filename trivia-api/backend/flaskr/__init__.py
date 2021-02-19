import os
from flask import Flask, request, abort, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


cors = CORS()
db = SQLAlchemy()
cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

# After_request decorator to set Access-Control-Allow
@app.after_request
def after_request(response: Response) -> Response:
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add(
        "Access-Control-Allow-Methods", "GET, PATCH, POST, DELETE, OPTIONS"
    )
    return response


# GET requests for all available categories - Completed
@app.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.to_dict()

    if len(categories) == 0:
        abort(404)

    return jsonify({"categories": categories, "success": True,})


# GET requests for questions including pagination (every 10 questions) - Completed
@app.route("/questions", methods=["GET"])
def get_questions():
    questions = Question.get_by_page(request, QUESTIONS_PER_PAGE)

    if len(questions) == 0:
        abort(404)

    return jsonify(
        {
            "questions": questions,
            "total_questions": len(Question.get_all()),
            "success": True,
            "categories": Category.to_dict(),
        }
    )


# Delete question using a question ID - Completed
@app.route("/questions/<int:question_id>", methods=["DELETE"])
def delete_question(question_id):
    question = Question.get_by_id(question_id)

    if question is None:
        abort(404)

    result = question.delete_record()

    if result["error"]:
        abort(500)

    questions = Question.get_by_page(request, QUESTIONS_PER_PAGE)

    return jsonify(
        {
            "deleted": question_id,
            "questions": questions,
            "total_questions": len(Question.get_all()),
            "success": True,
        }
    )


# POST a new question endpoint - Completed
@app.route("/questions", methods=["POST"])
def create_question():
    data = request.get_json()
    question = Question(**data)
    result = question.insert_record()

    if result["error"]:
        abort(500)

    _id = result["id"]
    questions = Question.get_by_page(request, QUESTIONS_PER_PAGE)

    return jsonify(
        {
            "created": _id,
            "questions": questions,
            "total_questions": len(Question.get_all()),
            "success": True,
        }
    )


# POST endpoint to get questions based on a search term - Completed
@app.route("/questions/search", methods=["POST"])
def search_questions():
    search_term = request.get_json()["search_term"]
    questions = Question.search(search_term)

    if len(questions) == 0:
        abort(404)

    return jsonify(
        {"questions": questions, "total_questions": len(questions), "success": True,}
    )


# GET endpoint to get questions based on category.
@app.route("/categories/<int:category_id>/questions", methods=["GET"])
def questions_by_category(category_id):
    questions = Question.get_by_category_by_page(
        category_id, request, QUESTIONS_PER_PAGE
    )

    if len(questions) == 0:
        abort(404)

    return jsonify(
        {
            "questions": questions,
            "total_questions": len(Question.get_by_category(category_id)),
            "current_category": Category.get_by_id(category_id).type,
            "success": True,
        }
    )


# POST Endpoint to get questions to play the quiz - Completed
@app.route("/quizzes", methods=["POST"])
def quiz():
    data = request.get_json()
    previous_questions = data.get("previous_questions", [])
    category = data.get("quiz_category", None)

    if category is None:
        abort(400)

    question = Question.get_random(category["id"], previous_questions)

    if question is None:
        return jsonify({"success": True})

    return jsonify({"question": question, "success": True})


# Error handlers - Completed


@app.errorhandler(400)
def not_found(error):
    return (
        jsonify({"success": False, "error": 400, "message": "Bad request"}),
        404,
    )


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "Not found"}),
        404,
    )


@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
        422,
    )


@app.errorhandler(500)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 500, "message": "Internal server error",}),
        500,
    )


return app
