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
            "sequence": str(data["sequence"]),
            "current_question": int(data["current_question"]),
        }
        users_ref.push(to_update)


def get_current_question_from_firebase(regno: str) -> int:
    for item in users_ref.get():
        if item["regno"].casefold() == regno:
            selector = users_ref.child(item).get()
            return selector["current_question"]


def update_current_question_to_firebase(regno: str, question_number: int) -> None:
    for item in users_ref.get():
        if item["regno"].casefold() == regno:
            selector = users_ref.child(item).get()
            current_question_update = users_ref.child(item).child("current_question")
            current_question_update.update(question_number)
