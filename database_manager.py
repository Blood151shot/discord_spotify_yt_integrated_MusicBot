import json
import os


DATABASE_PATH = r"C:\Users\Tanvir Singh\OneDrive\Desktop\old desktop apps\desktop\intern\PROJECT\database\user.json"


def load_users():

    if not os.path.exists(DATABASE_PATH):
        return {}

    try:

        with open(DATABASE_PATH, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}


def save_user(discord_id, refresh_token):

    users = load_users()

    users[str(discord_id)] = {
        "refresh_token": refresh_token
    }

    os.makedirs(
        os.path.dirname(DATABASE_PATH),
        exist_ok=True
    )

    with open(DATABASE_PATH, "w") as file:

        json.dump(
            users,
            file,
            indent=4
        )