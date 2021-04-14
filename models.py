from collections import OrderedDict
from playhouse.shortcuts import model_to_dict

import sys
import csv
import os

from peewee import *


DATABASE = SqliteDatabase('chef_tools.db')


class BaseModel(Model):
    name = CharField(unique=True)
    ed_yield = FloatField()
    by_the_lb = BooleanField(default=True)

    class Meta:
        database = DATABASE
        order_by = ('name')

    def menu_select(self):
        menu_items = (self.select()
                      )
        ing_list = []
        for item in menu_items:
            ing_list.append(model_to_dict(item))
        return ing_list


class Protein(BaseModel):
    """All animal based proteins"""


class Vegetable(BaseModel):
    """All vegetables"""


class Fruit(BaseModel):
    """All fruit"""


class Herb(BaseModel):
    """"All herbs and spices"""


class Category(Model):
    name = CharField(unique=True)

    class Meta:
        database = DATABASE


def build_categories():
    try:
        categories = ["Vegetable", "Herb", "Fruit", "Protein"]
        for cat in categories:
            Category.create(name=cat)
    except IntegrityError:
        pass


def initial_fill(csv_file, to_model):
    try:
        with open(csv_file, newline="") as csvfile:
            inv_reader = csv.DictReader(csvfile, delimiter=",")
            rows = list(inv_reader)
            for ingredient in rows:
                ingredient["name"] = ingredient["Item"]
                if ingredient["UOM"] == "lbs" or ingredient["UOM"] == "lb":
                    ingredient["by_the_lb"] = True
                else:
                    ingredient["by_the_lb"] = False
                ingredient["ed_yield"] = (float(
                    ingredient["EY %"].strip("%"))/100)
                to_model.create(name=ingredient["name"],
                                ed_yield=ingredient["ed_yield"],
                                by_the_lb=ingredient["by_the_lb"]
                                )

    except IntegrityError:
        pass


def category_menu():
    """prompts user for a category, protein, fruit, veg, herb, then user is
    taken to corresponding menu to select exact item from category list"""
    prod_cats = get_menu(Category)
    choice = None
    while choice != 'q'.lower():
        try:
            menu = OrderedDict(prod_cats)
            print("\nEnter 'q' to quit.")
            for key, value in menu.items():
                print("{}) {}".format(key, value))
            choice = input("\nAction:  ").strip()
            try:
                if choice == "q".lower():
                    sys.exit()
                else:
                    choice = int(choice)
                    if choice == 1:
                        menu_loop(Vegetable)
                    elif choice == 2:
                        menu_loop(Herb)
                    elif choice == 3:
                        menu_loop(Fruit)
                    elif choice == 4:
                        menu_loop(Protein)

            except ValueError:
                print("Please enter a valid response.")
                continue

        except DoesNotExist:
            pass


def get_menu(_model):
    current = BaseModel.menu_select(_model)
    current_tups = []
    for item in current:
        current_tups.append((item["id"], item["name"],),)
    return current_tups


def get_servings(item):
    """get the number of servings"""
    servings = None
    try:
        if check_plural(item):
            servings = input(
                f"How many servings or individual "
                f"{item.name.lower()} called for?   ")
        else:
            servings = input(
                f"How many servings or individual "
                f"{item.name.lower()}s called for?   ")
    except ValueError:
        print("Enter an integer")
    return servings


def serving_size():
    """obtains and returns ounces for serving size"""
    size = None
    try:
        size = input("How many ounces per serving?   ")
    except ValueError:
        print("Ounces in integer form.")
    return size


def total_needed(total_qty, item):
    """move logic from inside menu loop to clean menu loop"""
    needed = round(
        float(total_qty) * (float(item.ed_yield + 1)
                            ))
    return needed


def check_plural(item):
    plural_check = item.name[-1]
    if plural_check != "s":
        return False
    else:
        return True


def menu_loop(_model):
    """Return to main menu."""
    choice = None
    while choice != 'q'.lower():
        try:
            menu = OrderedDict(get_menu(_model))
            print("\nEnter 'q' to quit.")
            for key, value in menu.items():
                print("{}) {}".format(key, value))
            choice = input("\nAction:  ").strip()
            choice = int(choice)
            try:
                item = (_model
                        .get_by_id(choice)
                        )
                servings = get_servings(item)
                if item.by_the_lb:
                    total_qty = (float(servings) * float(serving_size()))
                    amt_to_pur = total_needed(total_qty, item)
                    pounds = amt_to_pur // 16
                    ounces = amt_to_pur % 16
                    print(f"You need {pounds} lbs {ounces} oz of {item.name}!")
                else:
                    total_qty = int(servings)
                    amt_to_pur = total_needed(total_qty, item)
                    if check_plural(item):
                        print(f"Y'all need {amt_to_pur} {item.name.lower()}!")
                    else:
                        print(f"Y'all need {amt_to_pur} {item.name.lower()}s!")

            except DoesNotExist:
                pass
        except ValueError:
            print("Please enter a valid integer.")
            continue

        keep_going = input(
            "[R] returns to main menu, "
            "[C] Continue to check quantities."
        ).lower().strip()
        if keep_going == "c":
            clear()
            continue
        else:
            clear()
            category_menu()
    else:
        print("Peace!")
        sys.exit()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables(
        [Protein, Vegetable, Fruit, Herb, Category],
        safe=True
    )
    DATABASE.close()
