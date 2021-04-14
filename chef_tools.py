#!/usr/bin/env python3
import models


if __name__ == '__main__':
    models.initialize()
    models.build_categories()
    models.initial_fill("clean_data/veggies.csv", models.Vegetable)
    models.initial_fill("clean_data/fruit.csv", models.Fruit)
    models.initial_fill("clean_data/herbs.csv", models.Herb)
    models.initial_fill("clean_data/proteins.csv", models.Protein)
    models.category_menu()
