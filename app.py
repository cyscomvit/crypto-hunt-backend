import csv
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, session

from flask_session import Session
from csv_functions import (
    check_password,
    check_user_exists_in_csv,
    get_team_details,
    header,
    write_to_csv,
)
from firebase_functions import initialize_firebase_for_a_user
from miscellaneous import *
from questions import (
    generate_sequence_for_a_team,
    get_answer_for_a_question,
    get_current_question,
    get_question_for_a_question_number,
    str_sequence_to_int_list,
)
from spreadsheet import write_to_gsheet

# Initialize Flask app
app = Flask("Cyber Odessey " + __name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
@app.route("/index", methods=["GET"])
def index_page():
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register(data: dict = {}):
    if request.method == "POST":
        if not data:
            data["name"] = request.form["name"]
            data["regno"] = request.form["regno"].upper()
            data["email"] = request.form["email"]
            data["password"] = hasher(request.form["password"])
            data["phone"] = request.form["phone"]
            data["receiptno"] = request.form["receiptno"]

        data["uniqid"] = generate_uuid()
        data["sequence"] = generate_sequence_for_a_team()
        data["current_question"] = 1

        if check_user_exists_in_csv(data["regno"], data["uniqid"]):
            f = True
            message = "You have already registered!"
        else:
            f = True
            message = "You have successfully registered"
            row = [
                data["name"],
                data["regno"],
                data["email"],
                data["password"],
                data["phone"],
                data["receiptno"],
                data["uniqid"],
                str(data["sequence"]),
                data["current_question"],
            ]
            write_to_csv(data, filename="CyberRegistrations.csv", row=row)
            write_to_gsheet(
                row=row, spreadsheet_id=os.getenv("REGISTRATIONS_SPREADSHEET")
            )
            initialize_firebase_for_a_user(data)
            print(f"Added {row}")
            session["name"] = data["name"]
            session["regno"] = data["regno"]
            session["uniqid"] = data["uniqid"]
            session["current_question"] = data["current_question"]
            return render_template(
                "register.html",
                show_message=message,
                filled=f,
            )
    return render_template("register.html", yet_to_register=True, filled=False)


@app.route("/login", methods=["POST", "GET"])
@app.route("/login.html", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        regno = request.form["regno"]
        password = hasher(request.form["password"])
        user_exists, password_correct = check_password(regno, password)
        if user_exists:
            if password_correct:
                row = get_team_details(regno)
                if row:
                    session["regno"] = row[header.index("regno")]
                    session["name"] = row[header.index("name")]
                    session["uniqid"] = row[header.index("uniqid")]
                    session["current_question"] = get_current_question(session["regno"])
                    return render_template(
                        "play.html",
                        question_text=get_question_for_a_question_number(
                            session["current_question"]
                        ),
                        name=session["name"],
                    )
                else:
                    return render_template(
                        "login.html",
                        error='User does not exist, please </a href="/register">register</a>!',
                    )
    else:
        return render_template("login.html", error="Wrong password. Try again")
    return render_template("login.html", error=None)


def check_answer(submitted_answer: str, question_no: int) -> bool:
    if get_answer_for_a_question(
        question_no
    ).casefold() == submitted_answer.casefold().replace(" ", ""):
        return True
    return False


@app.route("/play", methods=["GET", "POST"])
def play():
    if not session.get("name") or not session.get("current_question"):
        return render_template("login.html", error="Please login first")
    if request.method == "POST":
        ...
    else:
        session["answer_hash"] = hasher(
            get_answer_for_a_question(session["current_question"])
        )
        return render_template(
            "play.html",
            question_text=get_question_for_a_question_number(
                session["current_question"]
            ),
            name=session["name"],
            message="",
        )


load_dotenv("crypto.env")

if __name__ == "__main__":
    port = int(os.getenv("PORT")) if os.getenv("PORT") else 8080
    app.run(debug=bool(os.getenv("DEBUG")), host="0.0.0.0", port=port)
