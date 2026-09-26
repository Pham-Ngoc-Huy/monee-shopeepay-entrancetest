import pandas as pd


FILE_PATH = r"questions/260508_SPP BI Competency Test_v4_SA.xlsx"
SHEET_NAME = "1.1 SQL | Tables schema"


df_dim_user = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME,
    usecols="F:K",
    skiprows=27,
    nrows=7,
)

df_dim_user.to_csv(
    "raw_data/dim_user.csv",
    index=False,
)


df_dim_products = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME,
    usecols="F:P",
    skiprows=57,
    nrows=12,
)

df_dim_products.to_csv(
    "raw_data/dim_products.csv",
    index=False,
)


df_dwd_order = pd.read_excel(
    FILE_PATH,
    sheet_name=SHEET_NAME,
    usecols="F:T",
    skiprows=37,
    nrows=16,
)

df_dwd_order.to_csv(
    "raw_data/dwd_order.csv",
    index=False,
)


df_case_study_raw_material = pd.read_excel(
    FILE_PATH,
    sheet_name= "2.2 Case Study | Raw data"
)

df_case_study_raw_material.to_csv(
    "raw_data/case_study_raw_data.csv",
    index=False
)