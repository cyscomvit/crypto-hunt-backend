import csv
import os

import gspread
from dotenv import load_dotenv
from flask import Flask, render_template, request

app = Flask(__name__)

# Google Sheets API
def add_values_to_gsheet(
    spreadsheet_id: str,
    row: list,
    index: int = 2,
):
    gc = gspread.service_account(filename="YOUR_FILE_NAME.JSON")
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet_in_spreadsheet = spreadsheet.get_worksheet(0)
    sheet_in_spreadsheet.insert_row(values=row, index=index)


def write_to_gsheet(data: dict):
    row = [data["Name"], data["Regno"], data["Email"], data["Phone"], data["ReceiptNo"]]
    add_values_to_gsheet(
        spreadsheet_id="1qQrKjyvdyj6vcKQPnQsUKmxP2cWfkU7AwdITfB_f96E", row=row
    )


# CSV
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


def write_to_csv(data: dict):
    header = ["Name", "Regno", "Email", "Phone", "ReceiptNo"]

    row = [data["Name"], data["Regno"], data["Email"], data["Phone"], data["ReceiptNo"]]

    file_exists = check_if_exists_in_directory("CyberRegistrations.csv")

    with open("CyberRegistrations.csv", "a") as csv_file_obj:
        csv_write = csv.writer(csv_file_obj, delimiter=",", lineterminator="\n")
        if file_exists:
            csv_write.writerow(row)
        else:
            csv_write.writerow(header)
            csv_write.writerow(row)


def check_user_exists_in_csv(data: dict):
    if not check_if_exists_in_directory("CyberRegistrations.csv"):
        return False
    else:
        with open("CyberRegistrations.csv", "r") as csv_file_obj:
            csv_reader = csv.DictReader(csv_file_obj)
            for row in csv_reader:
                if data["Regno"] == row["Regno"]:
                    return True
            return False


@app.route("/")
def index_page():
    return render_template('index.html')


@app.route("/forms", methods=["POST", "GET"])
def data():
    data = {}
    if request.method == "POST":
        data["Name"] = request.form["Name"]
        data["Regno"] = request.form["Regno"].upper()
        data["Email"] = request.form["Email"]
        data["Phone"] = request.form["Phone"]
        
        data["ReceiptNo"] = request.form["ReceiptNo"]

        if check_user_exists_in_csv(data):
            return render_template(
                "forms.html", filled=True, show_message="You have already registered!"
            )
        else:
            write_to_csv(data)
            # write_to_gsheet(data)
            return render_template(
                "forms.html",
                show_message="You have successfully registered",
                filled=True,
            )

    return render_template(
        "forms.html", yet_to_register=True, filled=False
        )


if __name__ == "__main__":
    load_dotenv(".env")
    app.run(debug=bool(os.getenv("DEBUG")), host="0.0.0.0", port=80)