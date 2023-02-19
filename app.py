import csv
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect

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
def register():
    if request.method == "POST":
        data = {}
        data["name"] = request.form["name"]
        data["regno"] = request.form["regno"].upper()
        data["email"] = request.form["email"]
        data["password"] = hasher(request.form["password"])
        data["phone"] = request.form["phone"]
        data["receiptno"] = request.form["receiptno"]

        data["uniqid"] = generate_uuid()
        data["sequence"] = generate_sequence_for_a_team()
        data["current_question"] = data["sequence"][1]
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
                data["current_question"]
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
        password = hasher(request.form["password"])
        if check_password(regno, password):
            session["name"] = get_team_details(regno)["name"]
            session["password"] = get_team_details(regno)["password"]
            session["regno"] = regno
            session["uniqid"] = get_team_details(regno)["uniqid"]
            session["current_question"] = get_team_details(regno)["current_question"]
            return redirect("/play")

        else:
            return render_template("login.html", success=False, message="Invalid Credentials")
    return render_template("login.html", success=None)
            return render_template("play.html", success=True, name=session["name"])
        else:
            return render_template(
                "login.html", success=False, message="Invalid Credentials"
            )
    return render_template("login.html", success=None)


@app.route("/play", methods=["POST", "GET"])
def play():
    # if not logged in, redirect to login page
    if "regno" not in session:
        return render_template("login.html", success=None)

    # if already logged in, redirect to play page
    if "regno" in session:
        return render_template("play.html", success=True, name=session["name"])

    if request.method == "POST":
        answer = request.form["answer"]
        if answer == get_answer_for_a_question(session["current_question"]):
            session["current_question"] += 1
            return render_template("play.html", success=True, name=session["name"])
        else:
            return render_template("play.html", success=False, name=session["name"])

@app.route("/play",methods=["POST", "GET"])
def play():
    # if not logged in, redirect to login page
    if "regno" not in session:
        return render_template("login.html", success=None)
    
    # if already logged in, redirect to play page
    if "regno" in session:
        #TODO
        return render_template("play.html", success=True, name=session["name"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
    

load_dotenv("crypto.env")

if __name__ == "__main__":
    port = int(os.getenv("PORT")) if os.getenv("PORT") else 8080
    app.run(debug=bool(os.getenv("DEBUG")), host="0.0.0.0", port=port)
