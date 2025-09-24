#!/usr/bin/env python3
import argparse, os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(style="whitegrid")

def pick_col(df, lower, orig):
    """Return the column name that exists in df: prefer lower else orig, else None"""
    if lower in df.columns:
        return lower
    if orig in df.columns:
        return orig
    return None

def safe_save(fig, path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)

def main(args):
    df = pd.read_csv(args.input)
    out = args.out
    os.makedirs(out, exist_ok=True)

    # tolerant column detection (cleaned script used snake_case)
    monthly = pick_col(df, 'monthlyincome', 'MonthlyIncome')
    jobrole = pick_col(df, 'jobrole', 'JobRole')
    dept = pick_col(df, 'department', 'Department')
    age = pick_col(df, 'age', 'Age')
    attr = pick_col(df, 'attrition', 'Attrition')
    overtime = pick_col(df, 'overtime', 'OverTime') or pick_col(df, 'overtime', 'OverTime')

    # Ensure monthly is numeric if present
    if monthly:
        df[monthly] = pd.to_numeric(df[monthly], errors='coerce')

    # Basic cleaning for plotting purposes (don't drop everything)
    df = df.drop_duplicates()
    # Do not aggressively drop NA for all columns, only for plots that need them.

    print("Data shape:", df.shape)
    print("Detected columns - monthly:", monthly, "jobrole:", jobrole, "dept:", dept, "age:", age, "attrition:", attr)

    # ---------- 1) Attrition pie ----------
    if attr:
        counts = df[attr].value_counts()
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111)
        counts.plot.pie(autopct='%1.1f%%', startangle=90, ylabel='', ax=ax)
        ax.set_title('Attrition distribution')
        safe_save(fig, os.path.join(out, '01_attrition_pie.png'))

    # ---------- 2) Employees per Department (horizontal bar) ----------
    if dept:
        order = df[dept].value_counts().index
        fig = plt.figure(figsize=(8,5))
        ax = fig.add_subplot(111)
        sns.countplot(y=dept, data=df, order=order, ax=ax)
        ax.set_title('Employees per Department')
        safe_save(fig, os.path.join(out, '02_employees_per_department.png'))

    # ---------- 3) Stacked bar: Attrition by Department ----------
    if dept and attr:
        pivot = pd.crosstab(df[dept], df[attr])
        fig = pivot.plot(kind='bar', stacked=True, figsize=(8,5)).get_figure()
        fig.suptitle('Attrition by Department (stacked)')
        safe_save(fig, os.path.join(out, '03_attrition_by_department_stacked.png'))

    # ---------- 4) Monthly Income histogram + KDE ----------
    if monthly:
        fig = plt.figure(figsize=(8,5))
        ax = fig.add_subplot(111)
        sns.histplot(df[monthly].dropna(), bins=30, kde=True, ax=ax)
        ax.set_title('Monthly Income distribution')
        safe_save(fig, os.path.join(out, '04_monthlyincome_hist_kde.png'))

    # ---------- 5) Scatter: MonthlyIncome vs Age colored by Attrition ----------
    if monthly and age:
        df_sc = df[[age, monthly, attr]].dropna() if attr else df[[age, monthly]].dropna()
        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        if attr:
            sns.scatterplot(data=df_sc, x=age, y=monthly, hue=attr, alpha=0.7, ax=ax)
        else:
            sns.scatterplot(data=df_sc, x=age, y=monthly, alpha=0.7, ax=ax)
        ax.set_title('MonthlyIncome vs Age')
        safe_save(fig, os.path.join(out, '05_monthlyincome_vs_age_scatter.png'))

    # ---------- 6) Boxplot: MonthlyIncome by JobRole ----------
    if jobrole and monthly:
        fig = plt.figure(figsize=(12,6))
        ax = fig.add_subplot(111)
        sns.boxplot(x=jobrole, y=monthly, data=df, ax=ax)
        ax.set_title('Monthly Income by Job Role')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        safe_save(fig, os.path.join(out, '06_income_by_jobrole_boxplot.png'))

    # ---------- 7) Violin: Income distribution by Department ----------
    if dept and monthly:
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111)
        sns.violinplot(x=dept, y=monthly, data=df, ax=ax)
        ax.set_title('Income distribution by Department')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        safe_save(fig, os.path.join(out, '07_income_by_department_violin.png'))

    # ---------- 8) Annotated correlation heatmap (numeric features) ----------
    num = df.select_dtypes(include=['int64','float64'])
    if num.shape[1] > 1:
        corr = num.corr()
        fig = plt.figure(figsize=(10,8))
        ax = fig.add_subplot(111)
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlBu', ax=ax)
        ax.set_title('Correlation matrix (numeric)')
        safe_save(fig, os.path.join(out, '08_correlation_matrix_annot.png'))

    # ---------- 9) Pairplot (sample of numeric features) ----------
    if num.shape[1] > 2 and len(num) > 10:
        sample = num.sample(n=min(200, len(num)), random_state=1)
        g = sns.pairplot(sample)
        g.fig.suptitle('Pairplot (sampled numeric features)', y=1.02)
        g.savefig(os.path.join(out, '09_pairplot_sample.png'))
        plt.close('all')

    print("Saved plots into:", out)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='input csv path')
    parser.add_argument('--out', default='outputs/plots_extra', help='output folder for plots')
    args = parser.parse_args()
    main(args)
