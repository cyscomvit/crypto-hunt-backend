import csv
import os

from dotenv import load_dotenv
from firebase_functions import initialize_firebase_for_a_user
from flask import Flask, render_template, request, session
from flask_session import Session
from questions import (
    generate_sequence_for_a_team,
    str_sequence_to_list_int,
    get_answer_for_a_question,
    get_current_question,
    get_question_for_a_question_number,
)
from spreadsheet import write_to_gsheet
from miscellaneous import *

# Initialize Flask app
app = Flask("Cyber Odessey " + __name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


def check_if_exists_in_directory(file_or_folder_name: str, directory: str = "") -> bool:
    current_working_dir = os.getcwd()
    try:
        if directory:
            os.chdir(directory)
        return file_or_folder_name in os.listdir()
    except FileNotFoundError:
        return False
    finally:
        os.chdir(current_working_dir)


def write_to_csv(data: dict, row, filename: str = "CyberRegistrations.csv"):
    header = [
        "name",
        "regno",
        "email",
        "password",
        "phone",
        "receiptno",
        "uniqid",
        "sequence",
        "current_question",
    ]

    file_exists = check_if_exists_in_directory(filename)

    with open(filename, "a") as csv_file_obj:
        csv_write = csv.writer(csv_file_obj, delimiter=",", lineterminator="\n")
        if file_exists:
            csv_write.writerow(row)
        else:
            csv_write.writerow(header)
            csv_write.writerow(row)


def check_user_exists_in_csv(data: dict, filename: str = "CyberRegistrations.csv"):
    if not check_if_exists_in_directory(filename):
        return False
    else:
        with open(filename, "r") as csv_file_obj:
            csv_reader = csv.DictReader(csv_file_obj)
            for row in csv_reader:
                if data["regno"] == row["regno"]:
                    return True
                elif data["uniqid"] == row["uniqid"]:
                    return True
            return False


def check_password(username: str, password: str) -> tuple[bool, bool]:
    if not check_if_exists_in_directory("CyberRegistrations.csv"):
        return False
    else:
        user_exists = False
        with open("CyberRegistrations.csv", "r") as csv_file_obj:
            csv_reader = csv.DictReader(csv_file_obj)
            for row in csv_reader:
                if row["regno"] == username:
                    user_exists = True
                    if row["password"] == password:
                        return (user_exists, True)
                    else:
                        return (user_exists, False)
            return (user_exists, False)


def get_team_details(regno: str) -> list:
    if not check_if_exists_in_directory("CyberRegistrations.csv"):
        return False
    else:
        with open("CyberRegistrations.csv", "r") as csv_file_obj:
            csv_reader = csv.DictReader(csv_file_obj)
            for row in csv_reader:
                if row["regno"] == regno:
                    return row
            return []


@app.route("/")
@app.route("/index.html")
@app.route("/index")
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
        data["current_question"] = "1"

        if check_user_exists_in_csv(data):
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
            session["current_question"] = "1"
            return render_template(
                "register.html",
                show_message=message,
                filled=f,
            )
    return render_template("register.html", yet_to_register=True, filled=False)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["regno"]
        password = hasher(request.form["password"])
        _ = check_password(username, password)
        if _[0]:
            if _[1]:
                row = get_team_details()
                if row:
                    session["regno"] = row[1]
                    session["name"] = row[0]
                    session["current_question"] = get_current_question()
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
                        error='User does not exist, please </a href="./register">register</a>!',
                    )
    else:
        return render_template("login.html", error="Wrong password. Try again")
    return render_template("login.html", error=None)


def check_answer(user_id: str, question_no: int, answer: str):
    ...


@app.route("/submit", methods=["POST"])
def submit(user_id: str, question_no: int, answer: str):
    ...


@app.route("/play", methods=["GET", "POST"])
def play():
    if not session.get("name") and session.get("current_question"):
        return render_template("login.html")
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
        )


load_dotenv("crypto.env")

if __name__ == "a":
    port = int(os.getenv("PORT")) if os.getenv("PORT") else 8080
    app.run(debug=bool(os.getenv("DEBUG")), host="0.0.0.0", port=port)
