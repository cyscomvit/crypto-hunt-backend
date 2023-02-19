from firebase_admin import credentials, db, initialize_app
from os.path import dirname

config = {
    "database": {
        "firebaseDB": "https://cyber-odessey-default-rtdb.asia-southeast1.firebasedatabase.app/",
        "firebaseStorage": "vitask.appspot.com",
    }
}

# Initialize Firebase app
cred = credentials.Certificate(dirname(__file__) + "./credentials-cyber-odyssey.json")
initialize_app(
    cred,
    {
        "databaseURL": config["database"]["firebaseDB"],
        "storageBucket": config["database"]["firebaseStorage"],
    },
)

ref = db.reference("cyber-odessey")
users_ref = ref.child("users")


def initialize_firebase_for_a_user(data: dict):
    """
    data["Name"] = request.form["Name"]
    data["Regno"] = request.form["Regno"].upper()
    data["Email"] = request.form["Email"]
    data["Password"] = sha256(request.form["Password"]).hexdigest()
    data["Phone"] = request.form["Phone"]
    data["ReceiptNo"] = request.form["ReceiptNo"]
    data["UniqID"] = generate_uuid()
    """
    if "uniqid" in data:
        to_update = {
            "name": data["name"],
            "regno": data["regno"],
            "email": data["email"],
            "password": data["password"],
            "phone": data["phone"],
            "receiptno": data["receiptno"],
            "unidid": data["uniqid"],
            "sequence": str(data["sequence"]),
            "current_question": int(data["current_question"]),
        }
        users_ref.push(to_update)


def get_current_question_from_firebase(regno: str) -> int:
    all_users_data = users_ref.get()
    for item in all_users_data:
        if all_users_data[item]["regno"].casefold() == regno.casefold():
            selector = users_ref.child(item).get()
            return int(selector["current_question"])


def update_current_question_to_firebase(regno: str, question_number: int) -> None:
    all_users_data = users_ref.get()
    for item in all_users_data:
        if all_users_data[item]["regno"].casefold() == regno.casefold():
            data = users_ref.child(item).get()
            data["current_question"] = int(question_number)
            selector_update = users_ref.child(item)
            selector_update.update(data)


def get_points(regno: str) -> int:
    all_users_data = users_ref.get()
    for item in all_users_data:
        if all_users_data[item]["regno"].casefold() == regno.casefold():
            data = users_ref.child(item).get()
            if "points" in data:
                return int(data["points"])
            else:
                set_points(regno)
                return 0


def set_points(regno: str, points: int = 0):
    all_users_data = users_ref.get()
    for item in all_users_data:
        if all_users_data[item]["regno"].casefold() == regno.casefold():
            data = users_ref.child(item).get()
            data["points"] = points
            print(f"User {regno} has {points} points now")
            selector_update = users_ref.child(item)
            selector_update.update(data)


def add_points(regno: str, points: int = 0):
    set_points(regno, get_points(regno) + int(points))
