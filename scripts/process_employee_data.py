
"""process_employee_data.py
Read, clean, process and visualize an Employee/HR CSV.
Usage:
    python process_employee_data.py --input data/WA_Fn-UseC_-HR-Employee-Attrition.csv --out outputs/
Outputs produced:
  - cleaned_employee_data.csv
  - several PNG plots in outputs/
"""
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

def load_data(path):
    df = pd.read_csv(path)
    return df

def basic_report(df):
    print("DATA SHAPE:", df.shape)
    print('\nMISSING VALUES:\n', df.isnull().sum())
    print('\nDUPLICATES:', df.duplicated().sum())
    print('\nCOLUMN TYPES:\n', df.dtypes)

def clean_columns(df):
    # drop constant columns often present in IBM HR dataset
    for c in ['EmployeeCount','Over18','StandardHours']:
        if c in df.columns:
            df = df.drop(columns=[c])
    # normalize column names to snake_case
    df.columns = [c.strip().replace(' ', '_').replace('(', '').replace(')', '').lower() for c in df.columns]
    return df

def handle_missing(df):
    # For numeric columns: fill with median
    num_cols = df.select_dtypes(include=['int64','float64']).columns
    for c in num_cols:
        if df[c].isnull().any():
            df[c] = df[c].fillna(df[c].median())
    # For object/categorical: fill with mode
    cat_cols = df.select_dtypes(include=['object']).columns
    for c in cat_cols:
        if df[c].isnull().any():
            df[c] = df[c].fillna(df[c].mode().iloc[0])
    return df

def feature_engineering(df):
    # Age group
    if 'age' in df.columns:
        df['age_group'] = pd.cut(df['age'], bins=[17,25,35,45,55,100],
                                labels=['18-25','26-35','36-45','46-55','56+'])
    # salary band from monthly income if present
    if 'monthlyincome' in df.columns:
        try:
            df['salary_band'] = pd.qcut(df['monthlyincome'], q=4, labels=['Low','Medium','High','Very High'])
        except Exception:
            df['salary_band'] = pd.cut(df['monthlyincome'], bins=4, labels=['Low','Medium','High','Very High'])
    # simple binary map for overtime
    if 'overtime' in df.columns:
        df['overtime_flag'] = df['overtime'].map({'Yes':1, 'No':0})
    return df

def save_outputs(df, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, 'cleaned_employee_data.csv'), index=False)
    # Aggregations
    if 'department' in df.columns and 'monthlyincome' in df.columns:
        avg_salary = df.groupby('department')['monthlyincome'].mean().sort_values(ascending=False)
        avg_salary.to_csv(os.path.join(out_dir,'avg_monthly_income_by_department.csv'))
    # Plots
    # 1) Employees per Department
    if 'department' in df.columns:
        dept_count = df['department'].value_counts()
        plt.figure(figsize=(8,5))
        dept_count.plot(kind='bar')
        plt.title('Employees per Department')
        plt.xlabel('Department')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir,'employees_per_department.png'))
        plt.close()
    # 2) Monthly Income distribution
    if 'monthlyincome' in df.columns:
        plt.figure(figsize=(8,5))
        df['monthlyincome'].hist(bins=30)
        plt.title('Monthly Income Distribution')
        plt.xlabel('Monthly Income')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir,'monthlyincome_histogram.png'))
        plt.close()
    # 3) Boxplot: Monthly Income by JobRole (if present)
    if 'jobrole' in df.columns and 'monthlyincome' in df.columns:
        plt.figure(figsize=(10,6))
        df.boxplot(column='monthlyincome', by='jobrole', rot=45)
        plt.title('Monthly Income by Job Role')
        plt.suptitle('')
        plt.xlabel('Job Role')
        plt.ylabel('Monthly Income')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir,'monthlyincome_by_jobrole_boxplot.png'))
        plt.close()
    # 4) Correlation heatmap for numeric features
    num_cols = df.select_dtypes(include=['int64','float64']).columns
    if len(num_cols) > 1:
        corr = df[num_cols].corr()
        plt.figure(figsize=(10,8))
        plt.imshow(corr, aspect='auto')
        plt.colorbar()
        plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
        plt.yticks(range(len(corr.index)), corr.index)
        plt.title('Correlation Matrix (numeric features)')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir,'correlation_matrix.png'))
        plt.close()

def main(args):
    df = load_data(args.input)
    basic_report(df)
    df = clean_columns(df)
    df = df.drop_duplicates()
    df = handle_missing(df)
    df = feature_engineering(df)
    save_outputs(df, args.out)
    print('\nSaved cleaned CSV and plots to', args.out)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Path to CSV input')
    parser.add_argument('--out', default='outputs', help='Output directory')
    args = parser.parse_args()
    main(args)


"""
Short explanation of the graphs you’ll get:

Attrition pie — how many employees left vs stayed (quick attrition rate).

Employees per Department — headcount per department (horizontal bar).

Attrition by Department (stacked) — compare attrition counts across departments.

Monthly Income histogram + KDE — salary distribution and density.

Scatter (MonthlyIncome vs Age) — see correlation / clusters (color by attrition if available).

Boxplot Income by JobRole — median, IQR and outliers per job role.

Violin Income by Department — full distribution shape per department.

Annotated Correlation Heatmap — numeric feature correlations (helpful for ML).

Pairplot (sample) — pairwise relationships between numeric columns.
"""