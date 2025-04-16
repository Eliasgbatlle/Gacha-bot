import json
import os

DATA_FILE = "data/data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_data(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "coins": 0,
            "cards": [],
            "reputation": 0,
            "faction": None
        }
        save_data(data)
    return data[str(user_id)]

def add_coins(user_id, amount):
    data = load_data()
    user_data = get_user_data(user_id)
    user_data["coins"] += amount
    data[str(user_id)] = user_data
    save_data(data)

def get_balance(user_id):
    user_data = get_user_data(user_id)
    return user_data["coins"]

def daily_reward(user_id):
    reward = 500
    add_coins(user_id, reward)
    return reward

def get_user_cards(user_id):
    user_data = get_user_data(user_id)
    return user_data["cards"]

def add_card(user_id, card_name):
    user_data = get_user_data(user_id)
    if card_name not in user_data["cards"]:
        user_data["cards"].append(card_name)
        data = load_data()
        data[str(user_id)] = user_data
        save_data(data)
        return True
    return False

def work(user_id):
    earnings = 300
    user_data = get_user_data(user_id)
    rep = user_data["reputation"]
    bonus = int(earnings * (rep / 100)) if rep > 0 else 0
    total = earnings + bonus
    add_coins(user_id, total)
    user_data["reputation"] += 1
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)
    return total, user_data["reputation"]

def crime(user_id):
    earnings = 700
    user_data = get_user_data(user_id)
    penalty = int(earnings * 0.1)
    total = earnings - penalty
    add_coins(user_id, total)
    user_data["reputation"] -= 3
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)
    return total, user_data["reputation"]
