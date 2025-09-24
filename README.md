
# Employee Management — Data cleaning & visualization project

**What's included**
- `data/WA_Fn-UseC_-HR-Employee-Attrition.csv` (original dataset you uploaded)
- `scripts/process_employee_data.py` — a ready-to-run cleaning & plotting script
- `outputs/` — folder that will contain `cleaned_employee_data.csv` and PNG plots after running the script
- `requirements.txt`

**Run locally**
1. Create a Python virtual environment:
   `python -m venv venv && source venv/bin/activate`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run the script:
   `python scripts/process_employee_data.py --input data/WA_Fn-UseC_-HR-Employee-Attrition.csv --out outputs/`

The script will print a short report, save `cleaned_employee_data.csv` and several plots inside `outputs/`.
