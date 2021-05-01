import random
import asyncio
from SharedFiles.firebase_db import get_an_item, get_item_from_inventory

# return -1 if item is non existant
# return -2 if user does not have item
# return -3 is item is unusable
def use_item(item_id, user_id):
    item_id.lower()
    item = get_an_item(item_id)
    if not item:
        return -1
    if get_an_item(item_id) == -3:
        return -2
    item_name = item.get("item_name")


# all items that do things, and stuff
def clover(user_id):

    # checks if item is already active, if so return -1

    # add multiplier
    print("multiplier added!")
