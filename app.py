import logging
import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session

from csv_functions import check_user_exists_in_csv, header, write_to_csv
from firebase_functions import (
    check_password,
    get_ordered_list_of_users_based_on_points,
    get_team_details,
    update_team_details,
    get_team_dict,
    initialize_firebase_for_a_user,
)
from flask_session import Session
from miscellaneous import *
from questions import (
    generate_sequence_for_a_team,
    get_answer_for_a_question,
    get_personal_current_question,
    perhaps_completed
)
from spreadsheet import write_to_gsheet

# Initialize Flask app
app = Flask("Cyber Odessey " + __name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


def log_and_print(msg: str, level: str = "warn") -> None:
    """
    This function can be used for printing an error message, as well as for logging it by passing the level to the level parameter.

    This function looks for the env variable `KEEP_A_LOG`, to check whether it should keep logs to the file.

    Printing always happens, irrespective of the value of `KEEP_A_LOG`.

    #### Parameters
        `msg` - The message to print/log.
        `
    """
    print(msg)
    logger = logging.getLogger("cyberodyssey")
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        filename="cyber-odyssey.log",
        encoding="utf-8",
        level=logging.DEBUG,
    )
    if level == "warn":
        logger.warning(msg)
    elif level == "critical":
        logger.critical(msg)
    elif level == "info":
        logger.info(msg)
    else:
        logger.debug(msg)


@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
@app.route("/index", methods=["GET"])
def index_page():
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    message = ""
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
        data["current_question"] = 1
        data["sequence"] = str(team_sequence)
        data["completed"] = False
        print(data["current_question"])
        print(data["regno"] + " - " + data["name"], "tried to register")
        if check_user_exists_in_csv(data["regno"], data["uniqid"]):
            message = "You have already registered!"
            if not get_team_dict(data["regno"]):
                message = "Error in registering"
        else:
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
            message = "You have successfully registered"
        return render_template(
            "register.html",
            yet_to_register=False,
            show_message=message,
        )
    # 👇 Requested /register in a get method, return normally
    return render_template("register.html", yet_to_register=True, show_message=message)


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
            session["regno"] = d["regno"]
            session["uniqid"] = d["uniqid"]
            session["current_question"] = d["current_question"]
            print(
                f"User {session['regno']} has logged in, is on {session['current_question']} question"
            )
            return redirect("/play")

        else:
            return render_template("login.html", show_message="Invalid Credentials")
    return render_template("login.html", show_message="")


@app.route("/play", methods=["POST", "GET"])
def play():
    # if not logged in, redirect to login page
    if "regno" not in session:
        print("Not logged in and tried to access play")
        return redirect("/logout")

    show_name = session["name"] if "name" in session else session["regno"]

    attempted_correct = [False, False]

    if perhaps_completed(session['regno'],session['current_question']):
        return redirect("/completed")

    ques = get_personal_current_question(regno=session["regno"])

    # Post method, meaning sent answer, didn't request page. Just calculates whether right answer or not and returns the page.
    if request.method == "POST":
        attempted_correct[0] = True
        submitted_answer = request.form["answer"]

        log_and_print(
            f"{session['regno']} - {session['name']} answered {submitted_answer} for {ques.no} in list, {session['current_question']} in his sequence"
        )

        if submitted_answer == ques.answer:
            attempted_correct[1] = True
            session["current_question"] = str(int(session["current_question"]) + 1)
            update_team_details(
                session["regno"], "current_question", int(session["current_question"])
            )
            ques = get_personal_current_question(regno=session["regno"])
        else:
            attempted_correct[1] = False
        if perhaps_completed(session['regno'],session['current_question']):
            return redirect("/completed")

        return render_template(
            "play.html",
            show_name=show_name,
            attempted_correct=attempted_correct,
            q_type=ques.type,
            question=ques.text,
            ques_no=str(session["current_question"]),
        )

    # if already logged in, redirect to play page
    # Display the current question
    return render_template(
        "play.html",
        show_name=show_name,
        attempted_correct=attempted_correct,
        q_type=ques.type,
        question=ques.text,
        ques_no=str(session["current_question"]),
    )


@app.route("/completed", methods=["GET"])
def completed():
    if "current_question" in session:
        if perhaps_completed(session['regno'],session['current_question']):
            return render_template("completed.html")
    return redirect("/play")


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
