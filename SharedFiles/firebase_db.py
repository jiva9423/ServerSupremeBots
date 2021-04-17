import pyrebase
import time
import SharedFiles.fb_tokens as fb_tokens

config = fb_tokens.get_config()
email = fb_tokens.get_email()
password = fb_tokens.get_password()

fb = pyrebase.initialize_app(config)
auth = fb.auth()
user = auth.sign_in_with_email_and_password(email, password)  # get user
time_when_refresh = time.time() + int(user["expiresIn"])
user = auth.refresh(user['refreshToken'])
# get time when token needs to be refreshed
db = fb.database()  # get database


def init():
    global all_data
    all_data = {}

# before the 1 hour expiry: user = auth.refresh(user['refreshToken'])
# db.child("users").push(data, user['idToken'])
# db.child("users").child("members").set(data, user['idToken'])
# result = db.child("users").child("members").get(user['idToken'])


# refreshes token if needed
def refresh_token():
    global user
    global time_when_refresh
    global all_data
    if all_data is None:
        all_data = get_all_data()
    auth.refresh(user['refreshToken'])
    # refreshes token if needed
    #if time.time() > time_when_refresh:
        #user = auth.refresh(user['refreshToken'])
        #user = auth.sign_in_with_email_and_password(email, password)  # get user
        #time_when_refresh = time.time() + int(user["expiresIn"])


# ---------USER FUNCTIONS----------

def get_all_data():
    return db.get(user['idToken']).val()


# adds a user to the b
def create_user(user_id, inviter_id):
    global all_data
    # refreshes token if needed
    refresh_token()
    # check if user already created an verified. If so return false
    if is_user_in_fief(user_id):
        return False

    # create our user in the database
    user_data = {
        "verified": False,
        "user_id": user_id,
        "fief_id": -1,
        "wallet_bal": 100,
        "bank_bal": 0,
        "bank_max_space": 100,
        "num_of_invites": 0,
        "inviter_id": inviter_id,
        "level": 1,
        "xp": 0,
        "max_xp": 100,
        "inventory": {}
    }

    all_data["users"][user_id] = user_data # added tp data dictionary
    db.child("users").child(user_id).set(user_data, user['idToken'])
    print("user created")
    return True


# return true if user already exists in db and false if not
def user_exists(user_id):
    global all_data
    user_id = str(user_id)
    data = get_user_data(user_id)
    if data is None:
        print("User/Inviter", user_id, " does not exist in the database")
        return False
    return True


# returns the users data
def get_user_data(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    data = all_data.get("users").get(user_id)  # added tp data dictionary
    #data = db.child("users").child(user_id).get(user['idToken'])
    if data is None:
        return data
    return data


# --------FIEF USER FUNCTIONS-----------


# adds a user to a fief
def join_fief(user_id, fief_id):
    global all_data
    # refreshes token if needed
    refresh_token()
    user_id = str(user_id)
    # check if user exists in the db
    if not user_exists(user_id):
        create_user(user_id, 0)

    # check if user already created. If so return false
    if is_user_in_fief(user_id):
        return False

    # db.child("users").child(user_id).set(user_data, user['idToken'])
    # create our user in the database
    user_data = {
        "verified": True,
        "user_id": user_id,
        "fief_id": fief_id
    }

    all_data["users"][user_id]["verified"] = True
    all_data["users"][user_id]["user_id"] = user_id
    all_data["users"][user_id]["fied_id"] = fief_id

    db.child("users").child(user_id).update(user_data, user['idToken'])
    print("joined fief")

    return True


# check if user already assigned a fief
def is_user_in_fief(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return False
    # user will be set to active if in a fief
    #verified = db.child("users").child(user_id).child("verified").get(user['idToken'])
    verified = all_data.get("users").get(user_id).get("verified")
    if verified is None:
        return False
    return verified


# gets a users fief id, returns -1 if not in fief
def get_user_fief_id(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    # fief_id = db.child("users").child(user_id).child("fief_id").get(user['idToken'])
    fief_id = all_data.get("users").get(user_id).get("fief_id")
    if fief_id is None:
        return -1
    return fief_id


# ---------INVITE FUNCTIONS----------


# gets id of person who invited user
def get_inviter_id(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    # inviter_id = db.child("users").child(user_id).child("inviter_id").get(user['idToken'])
    inviter_id = all_data.get("users").get(user_id).get("inviter_id")
    if inviter_id is None:
        return -1
    return inviter_id


# increments user invites by 1
def increment_num_invites(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    # this person was not invited by anyone
    # (This should only happen to people in the server while the bot is being developed)
    if user_id == 0:
        return False

    if not user_exists(user_id):
        create_user(user_id, inviter_id=0)
        return False
    #num_of_invites = db.child("users").child(user_id).child("num_of_invites").get(user['idToken'])
    num_of_invites = all_data.get("users").get(user_id).get("num_of_invites")
    db.child("users").child(user_id).update({"num_of_invites": int(num_of_invites) + 1}, user['idToken'])
    all_data["users"][user_id]["num_of_invites"] = int(num_of_invites) + 1
    return True


# -------BAL FUNCTIONS---------


# sets a users balance (This will override bal to whatever you set the val to)
# if val < 0 then val set to 0
# return -1 if user doesn't exist otherwise return val bal was set to
def set_wallet_bal(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    if val <= 0:
        val = 0

    db.child("users").child(user_id).update({"wallet_bal": val}, user['idToken'])
    all_data["users"][user_id]["wallet_bal"] = val
    return val


# adds val to current bal. Lowest bal can be is 0
# if new_bal < 0 then bal set to 0
# return -1 if user doesn't exist otherwise return bal.
def add_wallet_bal(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    #new_bal = db.child("users").child(user_id).child("wallet_bal").get(user['idToken'])
    new_bal = all_data["users"][user_id]["wallet_bal"]
    new_bal = int(new_bal) + val

    if new_bal <= 0:
        new_bal = 0

    db.child("users").child(user_id).update({"wallet_bal": new_bal}, user['idToken'])
    new_bal = all_data["users"][user_id]["wallet_bal"] = new_bal
    return new_bal


# subtracts val from current bal. Lowest bal can be is 0.
# if new_bal < 0 then bal set to 0
# return -1 if user doesn't exist otherwise return bal.
def sub_wallet_bal(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    #new_bal = db.child("users").child(user_id).child("wallet_bal").get(user['idToken'])
    new_bal = all_data["users"][user_id]["wallet_bal"]
    new_bal = int(new_bal) - val

    if new_bal <= 0:
        new_bal = 0

    db.child("users").child(user_id).update({"wallet_bal": new_bal}, user['idToken'])
    new_bal = all_data["users"][user_id]["wallet_bal"] = new_bal
    return new_bal


# gets current user bal
# return -1 if user does not exist
def get_wallet_bal(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    # bal = db.child("users").child(user_id).child("wallet_bal").get(user['idToken'])
    bal = all_data.get("users").get(user_id).get("wallet_bal")
    return int(bal)


# ----------BANK METHODS---------


# get bank balance.
# returns -1 if user does not exist
def get_bank_bal(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    #bal = db.child("users").child(user_id).child("bank_bal").get(user['idToken'])
    bal = all_data.get("users").get(user_id).get("bank_bal")
    return int(bal)


# sets a users balance (This will override bal to whatever you set the val to)
# if val < 0 then val set to 0
# return -1 if user doesn't exist otherwise return val bal was set to
def set_bank_bal(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    if val <= 0:
        val = 0

    db.child("users").child(user_id).update({"bank_bal": val}, user['idToken'])
    all_data["users"][user_id]["bank_bal"] = val
    return val


# adds val to current bal. Lowest bal can be is 0
# if new_bal < 0 then bal set to 0
# return -1 if user doesn't exist otherwise return bal.
def add_bank_bal(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    #new_bal = db.child("users").child(user_id).child("bank_bal").get(user['idToken'])
    new_bal = all_data.get("users").get(user_id).get("bank_bal")
    new_bal = int(new_bal) + val

    if new_bal <= 0:
        new_bal = 0

    db.child("users").child(user_id).update({"bank_bal": new_bal}, user['idToken'])
    all_data["users"][user_id]["bank_bal"] = new_bal
    return new_bal


# subtracts val from current bal. Lowest bal can be is 0.
# if new_bal < 0 then bal set to 0
# return -1 if user doesn't exist otherwise return bal.
def sub_bank_bal(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    #new_bal = db.child("users").child(user_id).child("bank_bal").get(user['idToken'])
    new_bal = all_data.get("users").get(user_id).get("bank_bal")
    new_bal = int(new_bal) - val

    if new_bal <= 0:
        new_bal = 0

    db.child("users").child(user_id).update({"bank_bal": new_bal}, user['idToken'])
    all_data["users"][user_id]["bank_bal"] = new_bal
    return new_bal


# return 0 if successfully deposited to bank
# return -1 if user does not exist
# return -2 if val < 0
# return -3 if not enough money in wallet
# return -4 if not enough space in bank
def deposit_to_bank(user_id, val):
    global all_data
    refresh_token()
    if not user_exists(user_id):
        print("user doesn't exist")
        return -1

    if val < 0:
        print("can't deposit a negative amount")
        return -2

    wallet_bal = get_wallet_bal(user_id)
    bank_bal = get_bank_bal(user_id)
    max_bank_space = get_bank_space(user_id)

    if wallet_bal - val < 0:
        print("You don't have that much in your wallet")
        return -3

    if val + bank_bal > max_bank_space:
        print("You don't have enough space in the bank")
        return -4

    # subtract from wallet and add to bank
    sub_wallet_bal(user_id, val)
    add_bank_bal(user_id, val)
    return 0


# return 0 if successfully withdrawn from bank
# return -1 if user does not exist
# return -2 if val < 0
# return -3 if not enough money in bank
def withdraw_from_bank(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        print("user doesn't exist")
        return -1

    if val < 0:
        print("can't withdraw negative amount")
        return -2

    bank_bal = get_bank_bal(user_id)

    if bank_bal - val < 0:
        print("You don't have that much in your bank")
        return

    # subtract from bank and add to wallet
    sub_bank_bal(user_id, val)
    add_wallet_bal(user_id, val)
    return 0


# return bank space
# -1 if user does not exist
def get_bank_space(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        print("user doesn't exist")
        return -1

    # bank_space = db.child("users").child(user_id).child("bank_max_space").get(user['idToken'])
    bank_space = all_data.get("users").get(user_id).get("bank_max_space")
    return bank_space


# -------------XP METHODS-----------------


# get users xp.
# returns -1 if user does not exist
def get_xp(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    # xp = db.child("users").child(user_id).child("xp").get(user['idToken'])
    xp = all_data.get("users").get(user_id).get("xp")
    return int(xp)


# get users level.
# returns -1 if user does not exist
def get_level(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    # level = db.child("users").child(user_id).child("level").get(user['idToken'])
    level = all_data.get("users").get(user_id).get("level")
    return int(level)


# get max_xp for a user.
# returns -1 if user does not exist
def get_max_xp(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    # max_xp = db.child("users").child(user_id).child("max_xp").get(user['idToken'])
    max_xp = all_data.get("users").get(user_id).get("max_xp")
    return int(max_xp)


# set xp for a user, overrides current value.
# return 0 if set successfully
# return -1 if user does not exist
# return -2 if val < 0
def set_xp(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    if val < 0:
        return -2

    db.child("users").child(user_id).update({"xp": val}, user['idToken'])
    all_data["users"][user_id]["xp"] = val
    return 0


# set level for a user, overrides current value.
# return 0 if set successfully
# returns -1 if user does not exist
# return -2 if val < 0
def set_level(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    if val < 0:
        return -2

    db.child("users").child(user_id).update({"level": val}, user['idToken'])
    all_data["users"][user_id]["level"] = val
    return 0


# set max_xp for a user, overrides current value.
# return 0 if set successfully
# returns -1 if user does not exist
# return -2 if val < 0
def set_max_xp(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    if val < 0:
        return -2

    db.child("users").child(user_id).update({"max_xp": val}, user['idToken'])
    all_data["users"][user_id]["max_xp"] = val
    return 0


# return 1 if leveled up after adding xp
# return 0 if xp added successfully but no level up
# return -1 if user does not exist
# return -2 if val < 0
def add_xp(user_id, val):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    if val < 0:
        return -2

    leveled_up = False
    # add all the exp
    while val > 0:
        max_xp = get_max_xp(user_id)
        current_xp = get_xp(user_id)

        # check if we need to level up
        if current_xp + val >= max_xp:
            leveled_up = True
            # see how much xp was used for leveling
            xp_used = max_xp - current_xp
            # subtract what was used from the xp we received
            val -= xp_used
            # level  up
            level_up(user_id)
        else:
            current_xp += val
            # set users current xp
            set_xp(user_id, current_xp)
            val = 0

    # check if we leveled up
    if leveled_up:
        return 1

    return 0


# return 0 if successfully leveled up
# return -1 if user does not exist
def level_up(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    # increase level by one
    level = get_level(user_id)
    set_level(user_id, level + 1)

    # increase max_xp user needs to get
    max_xp = get_max_xp(user_id)
    set_max_xp(user_id, int(max_xp * 1.25))
    set_xp(user_id, 0)

    # increase bank bal

    # increase other stats
    return 0


# ----------INVENTORY METHODS--------

# return inventory as a dictionary
# return -1 if user does not exist
def get_inventory(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    # inv = db.child("users").child(user_id).child("inventory").get(user['idToken'])
    inv = all_data.get("users").get(user_id).get("inventory")

    if inv is None:
        return {}
    to_remove = []
    for key in inv:
        if inv[key] == 0:
            to_remove.append(key)

    for item in to_remove:
        inv.pop(item)

    return inv


# return the amount of this item the user has
# return -1 if user does not exist
# return -3 if item does not exist
def get_item_from_inventory(user_id, item_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    item_id = str(item_id).lower()
    if not user_exists(user_id):
        return -1

    items = get_items()

    if items.get(item_id) is None:
        return -3

    inv = get_inventory(user_id)

    # user does not have this item
    if inv.get(item_id) is None:
        return 0

    return inv.get(item_id)


# return 0 if item(s) added successfully
# return -1 if user does not exist
# return -2 if num < 0
# return -3 if item does not exist
def add_to_inventory(user_id, item_id, num=1):
    global all_data
    refresh_token()
    user_id = str(user_id)
    item_id = str(item_id).lower()
    if not user_exists(user_id):
        return -1

    if num < 0:
        return -2

    # check if item exists
    items = get_items()
    if items.get(item_id) is None:
        # item does not exist
        return -3

    # get inventory
    inv = get_inventory(user_id)

    # add item to the inventory
    if inv.get(item_id) is None:
        inv[item_id] = 1
    else:
        inv[item_id] += num

    db.child("users").child(user_id).update({"inventory": inv}, user['idToken'])
    all_data["users"][user_id]["inventory"] = inv
    return 0


# return 0 if item(s) removed successfully
# return -1 if user does not exist
# return -2 if num < 0
# return -3 if item does not exists
# return -4 if user does not have this item
# return -5 if user is trying to remove more of the item than they have
def remove_from_inventory(user_id, item_id, num=1):
    global all_data
    refresh_token()
    user_id = str(user_id)
    item_id = str(item_id).lower()
    if not user_exists(user_id):
        return -1

    if num < 0:
        return -2

    # check if item exists
    items = get_items()
    if items.get(item_id) is None:
        # item does not exist
        return -3

    # get inventory
    inv = get_inventory(user_id)

    # add item to the inventory
    if inv.get(item_id) is None:
        # you don't hve this item
        return -4
    else:
        if inv.get(item_id) - num < 0:
            # you don't have this many items to remove
            return -5
        inv[item_id] -= num

    db.child("users").child(user_id).update({"inventory": inv}, user['idToken'])
    all_data["users"][user_id]["inventory"] = inv
    return 0


# return 0 if inventory successfully cleared
# return -1 if user does not exist
def clear_inventory(user_id):
    global all_data
    refresh_token()
    user_id = str(user_id)
    if not user_exists(user_id):
        return -1

    db.child("users").child(user_id).update({"inventory": {}}, user['idToken'])
    all_data["users"][user_id]["inventory"] = {}
    return 0


# ----------ITEM METHODS--------


# return all items that exists as a dictionary
def get_items():
    global all_data
    refresh_token()
    #items = db.child("items").get(user['idToken'])
    items = all_data.get("items")

    if items is None:
        return {}

    return items


def get_items_by_type(type_name):
    global all_data
    refresh_token()
    # items = db.child("items").get(user['idToken'])
    item_types = all_data.get("item_types",{})
    items = item_types.get(type_name)

    if items is None:
        return {}

    if items.get("default") is not None:
        items.pop("default")

    return items


# gets rarest item from item type(s)
def get_rarest_item(max_rarity: int, *item_types):
    greatest_rarity = 0
    all_items = []

    for item_type in item_types:
        items_dict = get_items_by_type(item_type)
        item_list = list(items_dict.keys())
        for item in item_list:
            all_items.append(item)

    for item_id in all_items:
        item = get_an_item(item_id)
        item_rarity = int(item.get("item_rarity"))

        # if the item is the rarest so far and under the random limit for rarity, then set as the item
        if greatest_rarity < item_rarity < max_rarity:
            greatest_rarity = item_rarity
            chosen_item = item
    return chosen_item


# return item data
# return None if item does not exist
def get_an_item(item_id):
    global all_data
    refresh_token()
    items = get_items()
    item_id = str(item_id).lower()
    return items.get(item_id)


# Method adds an item to the item database
# item_id is a string id you want to give the item. This will be used to identify the item in the database.
# item_name is the name for the item
# description is the description for the item
# emoji is the emoji associated with the item
# buy_price is the cost to buy item from the shop. If buy_price is -1
# sell_price is what the user gets for selling the item. If type is not a type that allows selling this does not matter
# item_type is a string type for an item
# item_rarity is how rare the item is 1 is very common 100 is the rarest. Defaults to 1 if nothing is put in.
# overwrite is a boolean that determines if you want to overwrite existing item, defaults to False.
# if overwrite True it will overwrite the item with the same item_id.
# If False then will not create item if id already exists.
# return 1 if item added successfully with an item overwrite (item existed already and was replaced)
# return 0 if item added successfully with no item overwrite.
# return -1 if trying to overwrite an item when overwrite is set to False
# return -2 if invalid types were included in the item_types list
def add_item(item_id, item_name, description, emoji, buy_price, sell_price, item_type, item_rarity=1, overwrite=False):
    global all_data
    refresh_token()
    items = get_items()
    overwritten = False
    item_id = str(item_id).lower()
    # check if item id exists
    if items.get(item_id) is not None:
        # check if overwrite checked
        if not overwrite:
            print("Trying to overwrite already existing item with id", item_id, "with overwrite set to False")
            return -1
        overwritten = True

    types = get_all_item_types()

    if types.get(item_type) is None:
        print("Invalid type:", str(item_type))
        return -2

    buyable = True
    if buy_price < 0:
        buyable = False

    sellable = True
    if sell_price < 0:
        sellable = False

    item = {
        "item_id": item_id,
        "item_name": item_name,
        "description": description,
        "emoji":emoji,
        "item_rarity": item_rarity,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "item_type": item_type,
        "sellable": sellable,
        "buyable": buyable
    }



    # adds item.
    db.child("items").child(item_id).set(item, user['idToken'])
    all_data["items"][item_id] = item

    if overwritten:
        print("The item with item id", item_id, "was overwritten.")
        return 1

    update_item_type(item_type, item_id)
    # item successfully added
    print("No item was overwritten. New item with id", item_id, "was added.")
    return 0


# removes item from item database
# return 0 if item successfully removed
# return -1 if item does not exist in database
def remove_item(item_id):
    global all_data
    refresh_token()
    items = get_items()
    item_id = str(item_id).lower()
    if items.get(item_id) is None:
        return -1
    item = items.pop(item_id)
    remove_update_item_type(item.get("item_type"), item_id)
    db.child("items").set(items, user['idToken'])
    all_data["items"] = items
    # remove from item type
    return 0


# returns all the item types as a dictionary
def get_all_item_types():
    global all_data
    refresh_token()
    # types = db.child("item_types").get(user['idToken'])
    types = all_data.get("item_types")
    if types is None:
        return {}

    return types


def get_item_type(item_type):
    global all_data
    refresh_token()
    # types = db.child("item_types").child(item_type).get(user['idToken'])
    types = all_data.get("item_types").get(item_type)
    if types is None:
        return {}
    return types


def update_item_type(item_type, item_id):
    global all_data
    refresh_token()
    # add to item type
    items_with_type = get_item_type(item_type)
    items_with_type[item_id] = 1
    db.child("item_types").update({item_type: items_with_type}, user['idToken'])
    all_data["item_types"][item_type] = items_with_type
    return 0


def remove_update_item_type(item_type, item_id):
    global all_data
    refresh_token()
    # add to item type
    items_with_type = get_item_type(item_type)
    items_with_type.pop(item_id)
    db.child("item_types").update({item_type: items_with_type}, user['idToken'])
    all_data["item_types"][item_type] = items_with_type
    return 0


# return 0 if new item type was added to database
# return -1 if item type already exists
def add_item_type(item_type):
    global all_data
    refresh_token()
    types = get_all_item_types()

    if types.get(item_type) is not None:
        return -1

    types[item_type] = {"default":-1}
    db.child("item_types").set(types, user['idToken'])
    all_data["item_types"] = types
    return 0


# return 0 if successfully removed item type from database
# return -1 if item type does not exist
def remove_item_type(item_type):
    global all_data
    refresh_token()
    types = get_all_item_types()
    if types.get(item_type) is None:
        return -1

    types.pop(item_type)
    db.child("item_types").set(types, user['idToken'])
    all_data["item_types"] = types
    return 0


# --------------FIEF FUNCTIONS---------------


def create_fief_data(fief_name):
    global all_data
    fief_name = str(fief_name).lower()
    # create our user in the database
    fief_data = {
        "bank_bal": 0,
        "bank_max_space": 100,
        "num_of_invites": 0,
        "level": 1,
        "xp": 0,
        "max_xp": 100,
        "vault": {},
        "members": {},
        "tax_rate":15,
        "multiplier": 1,
        "number_of_wins": 1
    }

    all_data["fiefs"][fief_name] = fief_data  # added tp data dictionary
    db.child("fiefs").child(fief_name).set(fief_data, user['idToken'])


def fief_exists(fief_name):
    global all_data
    refresh_token()
    data = all_data.get(fief_name)
    if data is None:
        return False
    return True


# return fief data.
# if fief data doesn't exist for that fief it returns None.
def get_fief_data(fief_name):
    global all_data
    refresh_token()
    data = all_data.get("fiefs",{})
    fief_data = data.get(fief_name)
    return fief_data


# return 1 if leveled up after adding xp
# return 0 if xp added successfully but no level up
# return -1 if fief does not exist
# return -2 if val < 0
def add_fief_xp(fief_name, val):
    global all_data
    refresh_token()
    fief_id = str(fief_name)
    if not fief_exists(fief_id):
        return -1

    if val < 0:
        return -2

    leveled_up = False
    # add all the exp
    while val > 0:
        max_xp = get_fief_max_xp(fief_id)
        current_xp = get_fief_xp(fief_id)

        # check if we need to level up
        if current_xp + val >= max_xp:
            leveled_up = True
            # see how much xp was used for leveling
            xp_used = max_xp - current_xp
            # subtract what was used from the xp we received
            val -= xp_used
            # level  up
            level_up_fief(fief_id)
        else:
            current_xp += val
            # set users current xp
            set_fief_xp(fief_id, current_xp)
            val = 0

    # check if we leveled up
    if leveled_up:
        return 1

    return 0


# get fief xp
# return -1 if fief doesnt exist.
def get_fief_xp(fief_name):
    global all_data
    data = get_fief_data(fief_name)
    if data is None:
        return -1

    return data.get("xp")


# get max fief xp
# return -1 if fief doesnt exist.
def get_fief_max_xp(fief_name):
    global all_data
    data = get_fief_data(fief_name)
    if data is None:
        return -1
    return data.get("max_xp")


# get fief level
# return -1 if fief doesnt exist.
def get_fief_level(fief_name):
    global all_data
    data = get_fief_data(fief_name)
    if data is None:
        return -1
    return data.get("level")


def get_fief_bank(fief_name):
    global all_data
    data = get_fief_data(fief_name)
    if data is None:
        return -1
    return data.get("bank_bal")


def get_fief_bank_space(fief_name):
    global all_data
    data = get_fief_data(fief_name)
    if data is None:
        return -1
    return data.get("bank_max_space")


# set fief xp
# return 0 if successful
# return -1 if fief does not exist
# return -2 if val < 0
def set_fief_xp(fief_name, val):
    global all_data
    refresh_token()
    fief_id = str(fief_name)
    if not user_exists(fief_id):
        return -1

    if val < 0:
        return -2

    db.child("fiefs").child(fief_id).update({"xp": val}, user['idToken'])
    all_data["fiefs"][fief_id]["xp"] = val
    return 0


# set fief xp
# return 0 if successful
# return -1 if fief does not exist
# return -2 if val < 0
def set_fief_max_xp(fief_name, val):
    global all_data
    refresh_token()
    fief_id = str(fief_name)
    if not user_exists(fief_id):
        return -1

    if val < 0:
        return -2

    db.child("fiefs").child(fief_id).update({"max_xp": val}, user['idToken'])
    all_data["fiefs"][fief_id]["max_xp"] = val
    return 0


def set_fief_bank_space(fief_name, val):
    global all_data
    refresh_token()
    fief_id = str(fief_name)
    if not user_exists(fief_id):
        return -1

    if val < 0:
        return -2

    db.child("fiefs").child(fief_id).update({"bank_space": val}, user['idToken'])
    all_data["fiefs"][fief_id]["bank_space"] = val
    return 0


def set_fief_bank_bal(fief_name, val):
    global all_data
    refresh_token()
    fief_id = str(fief_name)
    if not user_exists(fief_id):
        return -1

    if val < 0:
        return -2

    db.child("fiefs").child(fief_id).update({"bank_bal": val}, user['idToken'])
    all_data["fiefs"][fief_id]["bank_bal"] = val
    return 0


# set fief xp
# return 0 if successful
# return -1 if fief does not exist
# return -2 if val < 0
def set_fief_level(fief_name, val):
    global all_data
    refresh_token()
    fief_id = str(fief_name)
    if not user_exists(fief_id):
        return -1

    if val < 0:
        return -2

    db.child("fiefs").child(fief_id).update({"level": val}, user['idToken'])
    all_data["fiefs"][fief_id]["level"] = val
    return 0


# set fief xp
# return 0 if successful
# return -1 if fief does not exist
# return -2 if val < 0
def level_up_fief(fief_name):
    global all_data
    refresh_token()
    fief_id = str(fief_name)
    if not user_exists(fief_id):
        return -1

    # increase level by one
    level = get_fief_level(fief_id)
    set_level(fief_id, level + 1)

    # increase max_xp user needs to get
    max_xp = get_fief_max_xp(fief_id)
    set_fief_max_xp(fief_id, int(max_xp * 1.25))
    set_fief_xp(fief_id, 0)

    # increase bank bal
    bank_space = int(get_fief_bank_space(fief_name)) * 1.25
    set_fief_bank_space(fief_name, bank_space)


    # increase vault size

    # increase other stats
    return 0







