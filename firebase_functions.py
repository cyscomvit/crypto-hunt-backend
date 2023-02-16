from firebase_admin import credentials, db, initialize_app

config = {
    "database": {
        "firebaseDB": "https://cyber-odessey-default-rtdb.asia-southeast1.firebasedatabase.app/",
        "firebaseStorage": "vitask.appspot.com",
    }
}

# Initialize Firebase app
cred = credentials.Certificate("./credentials-cyber-odyssey.json")
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
            "sequence":str(data["sequence"])
        }
        users_ref.push(to_update)

