# -*- coding: utf-8 -*-
"""
Created on Tue May 26 16:41:01 2026

@author: stevebc
"""

"""
generate_ingredient_prompts.py

Reads ingredient names from a CSV file and writes batched prompt text files,
each containing 100 ingredients formatted into a classification prompt.

Usage:
    python generate_ingredient_prompts.py
    python generate_ingredient_prompts.py --input path/to/file.csv --column clean_manual --batch-size 100 --output-dir prompts
"""

import csv
import os
import argparse
import math

# ── Canonical category-ingredient pairs ───────────────────────────────────────
CANONICAL_PAIRS = """category\tcanonical_ingredient
acid_citrus_vinegar\tunspecified
acid_citrus_vinegar\tbitter_orange
acid_citrus_vinegar\tcitrus
acid_citrus_vinegar\tlemon
acid_citrus_vinegar\tlime
alcohol\tunspecified
condiment_sauce\tunspecified
dairy\tbutter
dairy\tghee
dairy\tyogurt
dairy\tkefir
dairy\tmilk
dairy\tcream
dairy\tcheese
dairy\tunspecified
egg\tunspecified
eggs\tegg
fish_seafood\tmarine
fish_seafood\tfreshwater
fish_seafood\tunspecified
fish_seafood\tcrab
fruit\tunspecified
fruit\tacerola
fruit\tapple
fruit\tapricot
fruit\tavocado
fruit\tbabaco
fruit\tbanana
fruit\tberry
fruit\tblack_mulberry
fruit\tblack_raspberry
fruit\tblackberry
fruit\tblueberry
fruit\tbreadfruit
fruit\tbuffalo_currant
fruit\tcherimoya
fruit\tcherry
fruit\tchinese_bayberry
fruit\tcloudberry
fruit\tcommon_persimmon
fruit\tcranberry
fruit\tcupuau
fruit\tcurrant
fruit\tcurrant_black
fruit\tcurrant_red
fruit\tdates
fruit\tdurian
fruit\telderberry
fruit\tfig
fruit\tgarciniaindica
fruit\tgooseberry
fruit\tgrape
fruit\tgrapefruit
fruit\tgroundcherry
fruit\tguava
fruit\thogplum
fruit\thorned_melon
fruit\tjackfruit
fruit\tjapanese_persimmon
fruit\tjujube
fruit\tkiwi
fruit\tkumquat
fruit\tlitchi
fruit\tlongan
fruit\tloquat
fruit\tmalabar_plum
fruit\tmammee_apple
fruit\tmango
fruit\tmedlar
fruit\tmelon
fruit\tmulberry
fruit\tnanking_cherry
fruit\tnaranjilla
fruit\tolive
fruit\torange
fruit\tpapaya
fruit\tpassionfruit
fruit\tpeach
fruit\tpear
fruit\tpepino
fruit\tpersimmon
fruit\tpineapple
fruit\tplum
fruit\tpomegranate
fruit\tpummelo
fruit\tpurple_mangosteen
fruit\tquince
fruit\trambutan
fruit\traspberry
fruit\trhubarb
fruit\troseapple
fruit\tsapodilla
fruit\tsaskatoon_berry
fruit\tsoursop
fruit\tstarfruit
fruit\tstrawberry
fruit\ttamarind
grain_starch\tunspecified
grain_starch\tamaranth
grain_starch\tarrowhead
grain_starch\tbarley
grain_starch\tbuckwheat
grain_starch\tcassava
grain_starch\tcolocasia
grain_starch\tcorn_sweetcorn
grain_starch\tfrench_plantain
grain_starch\thard_wheat
grain_starch\tmillet
grain_starch\toats
grain_starch\tpotato
grain_starch\tquinoa
grain_starch\tred_rice
grain_starch\trice
grain_starch\tryeflour
grain_starch\tsago_palm
grain_starch\tsorghum
grain_starch\tspelt
grain_starch\tsweetpotato
grain_starch\ttaro
grain_starch\tteff
grain_starch\twheat
grain_starch\twild_rice
grain_starch\tyam
herb\tunspecified
herb\tangelica
herb\tbasil
herb\tborage
herb\tchive
herb\tcurryleaf
herb\tdandelion
herb\tdill
herb\tepazote
herb\tgarden_cress
herb\thops
herb\tlaurel
herb\tmint
herb\toregano
herb\tparsley
herb\troselle
herb\trosemary
herb\tsage
herb\tsorrel
herb\tsweet_grass
herb\tthyme
herb\tvalerian
invalid\tunspecified
leavening_thickener\tunspecified
leavening_thickener\tarrowroot
legume\tunspecified
legume\talfalfa
legume\tbeans
legume\tbeans_redkidneybeans
legume\tchickpea
legume\tclover
legume\tcowpeas
legume\tgram
legume\tgrass_pea
legume\tlentils
legume\tlupine
legume\tpeas
legume\tpigeonpea
legume\tsoybean
legume\twhite_lupine
liquid_stock\tunspecified
meat\tbeef
meat\tpork
meat\tmutton
meat\tunspecified
nut_seed\tunspecified
nut_seed\talmond
nut_seed\tbrazilnut
nut_seed\tcashew_nut
nut_seed\tchestnut
nut_seed\tchia
nut_seed\tcoconut
nut_seed\tcottonseed
nut_seed\tfilbert
nut_seed\tflaxseed
nut_seed\tgroundnut
nut_seed\thazelnut
nut_seed\tnuts
nut_seed\tpeanut
nut_seed\tpili_nut
nut_seed\tpistachio
nut_seed\tsesame
nut_seed\tsunflower
nut_seed\twalnut
oil_fat\tunspecified
oil_fat\toil_palm
oil_fat\trapeseed
oil_fat\tsafflower
other\tunspecified
other\tcocoa
other\tcoffee
other\tmate
other\ttea
poultry\tchicken
poultry\tunspecified
processed_prepared_food\tbread_wheaten
processed_prepared_food\tunspecified
spice\tallspice
spice\tanise
spice\tanise_staranise
spice\tcardamom
spice\tchili
spice\tcinnamon
spice\tclove
spice\tcoriander
spice\tcumin
spice\tfenugreek
spice\tginger
spice\thorseradish
spice\tliquorice
spice\tmustard
spice\tnigella
spice\tnutmeg
spice\tpepper
spice\tsaffron
spice\tturmeric
spice\tvanilla
spice\twasabi
spice\tunspecified
sweetener\tagave
sweetener\tcarob
sweetener\tsugar_substitute
sweetener\tunspecified
vegetable\tartichoke
vegetable\tasparagus
vegetable\tbamboo_shoots
vegetable\tbittergourd
vegetable\tcabbage
vegetable\tcarrot
vegetable\tcelery
vegetable\tchard
vegetable\tchicory
vegetable\tcucumber
vegetable\tcucurbita
vegetable\tdrumstick
vegetable\teggplant
vegetable\tendive
vegetable\tgarland_chrysanthemum
vegetable\tgarlic
vegetable\tgourd
vegetable\tjicama
vegetable\tjute
vegetable\tkenaf
vegetable\tlambsquarters
vegetable\tleek
vegetable\tlettuce
vegetable\tlotus
vegetable\tmalabar_spinach
vegetable\tmushroom
vegetable\tnew_zealand_spinach
vegetable\tnopal
vegetable\tokra
vegetable\tonion
vegetable\tparsnip
vegetable\tpumpkin
vegetable\tradish
vegetable\trocket_salad
vegetable\tspinach
vegetable\ttomato
vegetable\tturnip
vegetable\twaterchestnut
vegetable\twatercress
vegetable\twelsh_onion
vegetable\tunspecified"""

# ── Prompt template ────────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """\
please classify these {n} ingredients below:

{ingredient_list}

into one of the following 267 canonical category-ingredient pairs:

{canonical_pairs}

please return as a csv file that I can download with the same ID number as the text-file I pasted. there should be three columns: "ingredient" (the original ingredient name), "category", and "canonical ingredient". no fuzzy/logic/python matching. just take each ingredient on it's own and find your best judged match among the candidates below
"""


def read_ingredients(csv_path: str, column: str) -> list[str]:
    """Read all ingredient names from the specified column of a CSV file."""
    ingredients = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = row.get(column, "").strip()
            if val:
                ingredients.append(val)
    return ingredients


def write_prompt_file(
    ingredients: list[str],
    batch_index: int,
    output_dir: str,
    total_batches: int,
) -> str:
    """Write one prompt text file for a batch of ingredients."""
    ingredient_list = "\n".join(ingredients)
    n = len(ingredients)
    prompt = PROMPT_TEMPLATE.format(
        n=n,
        ingredient_list=ingredient_list,
        canonical_pairs=CANONICAL_PAIRS,
    )

    # Zero-pad batch number for clean alphabetical sorting of filenames
    pad = len(str(total_batches))
    filename = f"prompt_batch_{str(batch_index).zfill(pad)}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(prompt)

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Generate batched ingredient-classification prompt files."
    )
    parser.add_argument(
        "--input",
        default=r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_clean_manual_chatgpt.csv",
        help="Path to the input CSV file",
    )
    parser.add_argument(
        "--column",
        default="clean_manual",
        help="Name of the column containing ingredient names (default: clean_manual)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of ingredients per prompt file (default: 100)",
    )
    parser.add_argument(
        "--output-dir",
        default="prompts",
        help="Directory to write prompt files into (default: ./prompts)",
    )
    args = parser.parse_args()

    # ── Read ingredients ───────────────────────────────────────────────────────
    print(f"Reading '{args.column}' from: {args.input}")
    try:
        ingredients = read_ingredients(args.input, args.column)
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.input}")
        return
    except KeyError:
        print(f"ERROR: Column '{args.column}' not found in CSV.")
        return

    if not ingredients:
        print("No ingredients found. Check the column name and file contents.")
        return

    print(f"  → {len(ingredients)} ingredients loaded.")

    # ── Prepare output directory ───────────────────────────────────────────────
    os.makedirs(args.output_dir, exist_ok=True)

    # ── Split into batches and write prompt files ──────────────────────────────
    total_batches = math.ceil(len(ingredients) / args.batch_size)
    print(f"  → Writing {total_batches} prompt file(s) to '{args.output_dir}/'")

    for i in range(total_batches):
        batch = ingredients[i * args.batch_size : (i + 1) * args.batch_size]
        path = write_prompt_file(batch, i + 1, args.output_dir, total_batches)
        print(f"     Batch {i+1}/{total_batches}: {len(batch)} ingredients → {path}")

    print("\nDone.")


if __name__ == "__main__":
    main()