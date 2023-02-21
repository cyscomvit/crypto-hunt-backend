import csv
import os

from questions import (
    get_answer_for_a_question,
    get_current_question,
    update_current_question,
)

import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect

from flask_session import Session
from csv_functions import (
    check_user_exists_in_csv,
    header,
    write_to_csv,
)
from firebase_functions import (
    initialize_firebase_for_a_user,
    get_ordered_list_of_users_based_on_points,
    check_password,
    get_team_details,
    get_team_dict,
)
from miscellaneous import *
from questions import (
    generate_sequence_for_a_team,
    get_answer_for_a_question,
    get_current_question,
    get_question_for_a_question_number,
)
from spreadsheet import write_to_gsheet

# Initialize Flask app
app = Flask("Cyber Odessey " + __name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

_ = logging.getLogger("cyber odyssey")
logging.basicConfig(
    format="%(asctime)s %(message)s",
    filename="cyber-odyssey.log",
    encoding="utf-8",
    level=logging.DEBUG,
)


@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
@app.route("/index", methods=["GET"])
def index_page():
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        data = dict()
        data["name"] = request.form["name"]
        data["regno"] = request.form["regno"].casefold()
        data["email"] = request.form["email"]
        data["password"] = hasher(request.form["password"])
        data["phone"] = int(request.form["phone"])
        data["receiptno"] = int(request.form["receiptno"])

        data["uniqid"] = generate_uuid()
        team_sequence = generate_sequence_for_a_team()
        data["current_question"] = int(team_sequence[0])
        data["sequence"] = str(team_sequence)
        print(data["current_question"])
        print(data["regno"] + " - " + data["name"], "tried to register")
        if check_user_exists_in_csv(data["regno"], data["uniqid"]):
            filled = True
            message = "You have already registered!"
        else:
            filled = True
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
            write_to_gsheet(
                row=row, spreadsheet_id=os.getenv("REGISTRATIONS_SPREADSHEET")
            )
            initialize_firebase_for_a_user(data)
            write_to_csv(data, filename="CyberRegistrations.csv", row=row)
            print(f"Added {row}")
            session["name"] = data["name"]
            session["regno"] = data["regno"]
            session["uniqid"] = data["uniqid"]
            session["current_question"] = data["current_question"]
        return render_template(
            "register.html",
            yet_to_register=False,
            show_message=message,
            filled=filled,
        )
    # 👇 Requested /register in a get method, return normally
    return render_template("register.html", yet_to_register=True, filled=False)


@app.route("/login", methods=["POST", "GET"])
def login():
    # if already logged in, redirect to play page (Enable this after testing)

    # if "regno" in session:
    #     return render_template("play.html", success=True, name=session["name"])

    if request.method == "POST":
        regno = request.form["regno"].upper()
        hashed_pw = hasher(request.form["password"])
        print(regno + " - " + hashed_pw, "tried to login")
        if check_password(regno, hashed_pw):
            d = get_team_dict(regno)
            session["name"] = d["name"]
            session["password"] = d["password"]
            session["regno"] = d["regno"]
            session["uniqid"] = d["uniqid"]
            session["current_question"] = d["current_question"]
            print(session["current_question"])
            return redirect("/play")

        else:
            return render_template("login.html", show_message="Invalid Credentials")
    return render_template("login.html", show_message="")


@app.route("/play", methods=["POST", "GET"])
def play():
    # if not logged in, redirect to login page
    if "regno" not in session:
        return render_template("login.html", success=None)
    # if already logged in, redirect to play page
    # Display the current question
    current_question = get_current_question(session["regno"])
    # print(current_question)
    question = get_question_for_a_question_number(current_question)
    # print(question)
    if request.method == "POST":
        answer = request.form["answer"]
        if answer == get_answer_for_a_question(current_question):
            print(f"{session['regno']} - {session['name']} answered correctly")
            count += 1
            update_current_question(session["regno"], current_question)
            question = get_question_for_a_question_number(current_question)
            render_template(
                "play.html",
                success=True,
                name=session["name"],
                question=question,
                questionNumber=count,
            )
        else:
            print(f"{session['regno']} - {session['name']} answered incorrectly")
            render_template(
                "play.html",
                success=False,
                name=session["name"],
                question=question,
                questionNumber=count,
            )

    return render_template(
        "play.html",
        success=True,
        name=session["name"],
        question=question,
        questionNumber=count,
    )


@app.route("/leaderboard")
def leaderboard():
    ordered_list = get_ordered_list_of_users_based_on_points()
    return render_template("leaderboard.html", ordered_list=ordered_list)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


load_dotenv("crypto.env")

if __name__ == "__main__":
    port = int(os.getenv("PORT")) if os.getenv("PORT") else 8080
    app.run(debug=bool(os.getenv("DEBUG")), host="0.0.0.0", port=port)
