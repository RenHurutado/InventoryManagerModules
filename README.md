# InventoryManagerModules

LMstudio Compatible. Program optimized for Gemma 3-12b

Things to do before executing program 

Check file structure

# workshop_inventory/
├── database/
├── core/
├── llm/
├── reports/
├── ui/
├── utils/
├── localization/
└── data/
    ├── imports/
    └── exports/

Files needed

workshop_inventory/config.py
workshop_inventory/database/connection.py
workshop_inventory/database/setup.py
workshop_inventory/core/inventory.py
workshop_inventory/core/checkout.py
workshop_inventory/cli.py
workshop_inventory/main.py
workshop_inventory/requirements.txt

# run pip install -r requirements.txt

For first time csv import:

# run python main.py --import data/imports/your_file.csv 

otherwise: 

# run python main.py
