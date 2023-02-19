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
        reg_number_ref = users_ref.child(data["regno"].casefold())
        selector = reg_number_ref.get()
        if selector:
            if "name" in selector:
                print(f"user {data['regno']} already exists")
        else:
            if "points" not in data:
                data["points"] = 0
            reg_number_ref.update(data)
    else:
        print("uniq id not present")


def get_team_detail(regno: str, field_name: str, default_if_not_exist=None):
    regno = regno.casefold()
    reg_number_ref = users_ref.child(regno)
    selector = reg_number_ref.get()
    if selector:
        if field_name in selector:
            return selector[field_name]
        else:
            if default_if_not_exist:
                update_team_detail(regno, field_name, default_if_not_exist)
            return None
    else:
        return None


def update_team_detail(regno: str, field_name: str, field_value):
    regno = regno.casefold()
    reg_number_ref = users_ref.child(regno)
    selector = reg_number_ref.get()
    if not selector:
        selector = dict()
    selector[field_name] = field_value
    selector_update = reg_number_ref
    selector_update.update(selector)


def get_current_question_from_firebase(regno: str) -> int:
    return int(get_team_detail(regno, "current_question"))


def update_current_question_to_firebase(regno: str, question_number: int) -> None:
    update_team_detail(regno, "current_question", int(question_number))


def get_points(regno: str) -> int:
    return int(get_team_detail(regno, "points"))


def set_points(regno: str, points: int = 0):
    regno = regno.casefold()
    reg_number_ref = users_ref.child(regno)
    selector = reg_number_ref.get()
    if not selector:
        selector = dict()
    selector["points"] = points
    selector_update = reg_number_ref
    selector_update.update(selector)
    print(f"User {regno} has {points} points now")


def add_points(regno: str, points: int = 0):
    set_points(regno, get_points(regno) + int(points))


def get_ordered_list_of_users_based_on_points() -> list["str"]:
    # Returns a largest to smallest list of user based on their points
    all_users_ref = users_ref.get()
    users_and_points = {
        user: all_users_ref[user]["points"]
        for user in all_users_ref
        if user and "points" in all_users_ref[user]
    }
    print(users_and_points)
    sorted_users_and_points = sorted(
        users_and_points.items(), key=lambda x: x[1], reverse=True
    )
    return [user_and_points[0] for user_and_points in sorted_users_and_points]
