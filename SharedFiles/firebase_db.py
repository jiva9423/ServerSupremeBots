import pyrebase
import time
import fb_tokens

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


# before the 1 hour expiry: user = auth.refresh(user['refreshToken'])
# db.child("users").push(data, user['idToken'])
# db.child("users").child("members").set(data, user['idToken'])
# result = db.child("users").child("members").get(user['idToken'])


# refreshes token if needed
def refresh_token():
    global user
    global time_when_refresh
    auth.refresh(user['refreshToken'])
    # refreshes token if needed
    #if time.time() > time_when_refresh:
        #user = auth.refresh(user['refreshToken'])
        #user = auth.sign_in_with_email_and_password(email, password)  # get user
        #time_when_refresh = time.time() + int(user["expiresIn"])


# ---------USER FUNCTIONS----------


# adds a user to the b
def create_user(user_id, inviter_id):
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

    db.child("users").child(user_id).set(user_data, user['idToken'])
    print("user created")
    return True


# return true if user already exists in db and false if not
def user_exists(user_id):
    data = get_user_data(user_id)
    if data is None:
        print("User/Inviter", user_id, " does not exist in the database")
        return False
    return True


# returns the users data
def get_user_data(user_id):
    refresh_token()
    data = db.child("users").child(user_id).get(user['idToken'])
    if data is None:
        return data
    return data.val()


# --------FIEF FUNCTIONS-----------


# adds a user to a fief
def join_fief(user_id, fief_id):
    # refreshes token if needed
    refresh_token()

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

    db.child("users").child(user_id).update(user_data, user['idToken'])
    print("joined fief")

    return True


# check if user already assigned a fief
def is_user_in_fief(user_id):
    refresh_token()
    if not user_exists(user_id):
        return False
    # user will be set to active if in a fief
    verified = db.child("users").child(user_id).child("verified").get(user['idToken'])
    if verified is None:
        return False
    return verified.val()


# gets a users fief id, returns -1 if not in fief
def get_user_fief_id(user_id):
    refresh_token()
    fief_id = db.child("users").child(user_id).child("fief_id").get(user['idToken'])
    if fief_id is None:
        return -1
    return fief_id.val()


# ---------INVITE FUNCTIONS----------


# gets id of person who invited user
def get_inviter_id(user_id):
    refresh_token()
    inviter_id = db.child("users").child(user_id).child("inviter_id").get(user['idToken'])

    if inviter_id is None:
        return -1
    return inviter_id.val()


# increments user invites by 1
def increment_num_invites(user_id):
    refresh_token()
    # this person was not invited by anyone
    # (This should only happen to people in the server while the bot is being developed)
    if user_id == 0:
        return False

    if not user_exists(user_id):
        create_user(user_id, inviter_id=0)
        return False
    num_of_invites = db.child("users").child(user_id).child("num_of_invites").get(user['idToken'])
    db.child("users").child(user_id).update({"num_of_invites": int(num_of_invites.val()) + 1}, user['idToken'])
    return True


# -------BAL FUNCTIONS---------


# sets a users balance (This will override bal to whatever you set the val to)
# if val < 0 then val set to 0
# return -1 if user doesn't exist otherwise return val bal was set to
def set_wallet_bal(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    if val <= 0:
        val = 0

    db.child("users").child(user_id).update({"wallet_bal": val}, user['idToken'])
    return val


# adds val to current bal. Lowest bal can be is 0
# if new_bal < 0 then bal set to 0
# return -1 if user doesn't exist otherwise return bal.
def add_wallet_bal(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    new_bal = db.child("users").child(user_id).child("wallet_bal").get(user['idToken'])
    new_bal = int(new_bal.val()) + val

    if new_bal <= 0:
        new_bal = 0

    db.child("users").child(user_id).update({"wallet_bal": new_bal}, user['idToken'])
    return new_bal


# subtracts val from current bal. Lowest bal can be is 0.
# if new_bal < 0 then bal set to 0
# return -1 if user doesn't exist otherwise return bal.
def sub_wallet_bal(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    new_bal = db.child("users").child(user_id).child("wallet_bal").get(user['idToken'])
    new_bal = int(new_bal.val()) - val

    if new_bal <= 0:
        new_bal = 0

    db.child("users").child(user_id).update({"wallet_bal": new_bal}, user['idToken'])

    return new_bal


# gets current user bal
# return -1 if user does not exist
def get_wallet_bal(user_id):
    refresh_token()

    if not user_exists(user_id):
        return -1

    bal = db.child("users").child(user_id).child("wallet_bal").get(user['idToken'])
    return int(bal.val())


# ----------BANK METHODS---------


# get bank balance.
# returns -1 if user does not exist
def get_bank_bal(user_id):
    refresh_token()

    if not user_exists(user_id):
        return -1

    bal = db.child("users").child(user_id).child("bank_bal").get(user['idToken'])
    return int(bal.val())


# sets a users balance (This will override bal to whatever you set the val to)
# if val < 0 then val set to 0
# return -1 if user doesn't exist otherwise return val bal was set to
def set_bank_bal(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    if val <= 0:
        val = 0

    db.child("users").child(user_id).update({"bank_bal": val}, user['idToken'])
    return val


# adds val to current bal. Lowest bal can be is 0
# if new_bal < 0 then bal set to 0
# return -1 if user doesn't exist otherwise return bal.
def add_bank_bal(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    new_bal = db.child("users").child(user_id).child("bank_bal").get(user['idToken'])
    new_bal = int(new_bal.val()) + val

    if new_bal <= 0:
        new_bal = 0

    db.child("users").child(user_id).update({"bank_bal": new_bal}, user['idToken'])
    return new_bal


# subtracts val from current bal. Lowest bal can be is 0.
# if new_bal < 0 then bal set to 0
# return -1 if user doesn't exist otherwise return bal.
def sub_bank_bal(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    new_bal = db.child("users").child(user_id).child("bank_bal").get(user['idToken'])
    new_bal = int(new_bal.val()) - val

    if new_bal <= 0:
        new_bal = 0

    db.child("users").child(user_id).update({"bank_bal": new_bal}, user['idToken'])

    return new_bal


# return 0 if successfully deposited to bank
# return -1 if user does not exist
# return -2 if val < 0
# return -3 if not enough money in wallet
# return -4 if not enough space in bank
def deposit_to_bank(user_id, val):
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
    refresh_token()
    if not user_exists(user_id):
        print("user doesn't exist")
        return -1

    if val < 0:
        print("can't withdraw negative amount")
        return -2

    bank_bal = get_wallet_bal(user_id)

    if bank_bal - val < 0:
        print("You don't have that much in your bank")
        return

    # subtract from bank and add to wallet
    sub_bank_bal(user_id, val)
    add_wallet_bal(user_id, val)
    return 0


# return bank space or -1 if user does not exist
def get_bank_space(user_id):
    refresh_token()

    if not user_exists(user_id):
        print("user doesn't exist")
        return -1

    bank_space = db.child("users").child(user_id).child("bank_max_space").get(user['idToken'])
    return bank_space.val()


# -------------XP METHODS-----------------


# get users xp.
# returns -1 if user does not exist
def get_xp(user_id):
    refresh_token()

    if not user_exists(user_id):
        return -1

    xp = db.child("users").child(user_id).child("xp").get(user['idToken'])
    return int(xp.val())


# get users level.
# returns -1 if user does not exist
def get_level(user_id):
    refresh_token()

    if not user_exists(user_id):
        return -1

    level = db.child("users").child(user_id).child("level").get(user['idToken'])
    return int(level.val())


# get max_xp for a user.
# returns -1 if user does not exist
def get_max_xp(user_id):
    refresh_token()

    if not user_exists(user_id):
        return -1

    max_xp = db.child("users").child(user_id).child("max_xp").get(user['idToken'])
    return int(max_xp.val())


# set xp for a user, overrides current value.
# return 0 if set successfully
# return -1 if user does not exist
# return -2 if val < 0
def set_xp(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    if val < 0:
        return -2

    db.child("users").child(user_id).update({"xp": val}, user['idToken'])
    return 0


# set level for a user, overrides current value.
# return 0 if set successfully
# returns -1 if user does not exist
# return -2 if val < 0
def set_level(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    if val < 0:
        return -2

    db.child("users").child(user_id).update({"level": val}, user['idToken'])
    return 0


# set max_xp for a user, overrides current value.
# return 0 if set successfully
# returns -1 if user does not exist
# return -2 if val < 0
def set_max_xp(user_id, val):
    refresh_token()

    if not user_exists(user_id):
        return -1

    if val < 0:
        return -2

    db.child("users").child(user_id).update({"max_xp": val}, user['idToken'])
    return 0


# return 1 if leveled up after adding xp
# return 0 if xp added successfully but no level up
# return -1 if user does not exist
# return -2 if val < 0
def add_xp(user_id, val):
    refresh_token()

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
    refresh_token()

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
    refresh_token()

    if not user_exists(user_id):
        return -1

    inv = db.child("users").child(user_id).child("inventory").get(user['idToken'])

    if inv is None:
        return {}
    elif inv.val() is None:
        return {}

    return inv.val()


# return the amount of this item the user has
# return -1 if user does not exist
# return -3 if item does not exist
def get_item_from_inventory(user_id, item_id):
    refresh_token()
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

    return inv.val().get(item_id)


# return 0 if item(s) added successfully
# return -1 if user does not exist
# return -2 if num < 0
# return -3 if item does not exist
def add_to_inventory(user_id, item_id, num=1):
    refresh_token()
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
    return 0


# return 0 if item(s) removed successfully
# return -1 if user does not exist
# return -2 if num < 0
# return -3 if item does not exists
# return -4 if user does not have this item
# return -5 if user is trying to remove more of the item than they have
def remove_from_inventory(user_id, item_id, num=1):
    refresh_token()
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
    return 0


# return 0 if inventory successfully cleared
# return -1 if user does not exist
def clear_inventory(user_id):
    refresh_token()

    if not user_exists(user_id):
        return -1

    db.child("users").child(user_id).update({"inventory": {}}, user['idToken'])

    return 0


# ----------ITEM METHODS--------


# return all items that exists as a dictionary
def get_items():
    refresh_token()
    items = db.child("items").get(user['idToken'])

    if items is None:
        return {}
    elif items.val() is None:
        return {}

    return items.val()


# return item data
# return None if item does not exist
def get_an_item(item_id):
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
    refresh_token()
    items = get_items()
    item_id = str(item_id).lower()
    if items.get(item_id) is None:
        return -1
    item = items.pop(item_id)
    remove_update_item_type(item.get("item_type"), item_id)
    db.child("items").set(items, user['idToken'])
    # remove from item type
    return 0


# returns all the item types as a dictionary
def get_all_item_types():
    refresh_token()
    types = db.child("item_types").get(user['idToken'])
    if types is None:
        return {}
    elif types.val() is None:
        return {}

    return types.val()


def get_item_type(item_type):
    refresh_token()
    types = db.child("item_types").child(item_type).get(user['idToken'])
    if types is None:
        return {}
    elif types.val() is None:
        return {}
    return types.val()


def update_item_type(item_type, item_id):
    refresh_token()
    # add to item type
    items_with_type = get_item_type(item_type)
    items_with_type[item_id] = 1
    db.child("item_types").update({item_type: items_with_type}, user['idToken'])
    return 0


def remove_update_item_type(item_type, item_id):
    refresh_token()
    # add to item type
    items_with_type = get_item_type(item_type)
    items_with_type.pop(item_id)
    db.child("item_types").update({item_type: items_with_type}, user['idToken'])
    return 0


# return 0 if new item type was added to database
# return -1 if item type already exists
def add_item_type(item_type):
    refresh_token()
    types = get_all_item_types()

    if types.get(item_type) is not None:
        return -1

    types[item_type] = {"default":-1}
    db.child("item_types").set(types, user['idToken'])
    return 0


# return 0 if successfully removed item type from database
# return -1 if item type does not exist
def remove_item_type(item_type):
    refresh_token()
    types = get_all_item_types()
    if types.get(item_type) is None:
        return -1

    types.pop(item_type)
    db.child("item_types").set(types, user['idToken'])
    return 0





