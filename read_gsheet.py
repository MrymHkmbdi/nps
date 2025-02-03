# read_gsheet.py
import pandas as pd
import requests
from io import BytesIO


def fetch_gsheet_data():
    gsheet_link_thirdparty = "https://docs.google.com/spreadsheets/d/1WkC0A9qH6NikSwv0_HYv4l0EjIKwAb7PBjNEgDxnYcA/export?format=csv"
    response = requests.get(gsheet_link_thirdparty)
    data = response.content
    df_thirdparty = pd.read_csv(BytesIO(data), encoding='utf-8')
    df_thirdparty.to_csv('data/output_thirdparty.csv', index=False)

    gsheet_link_carbody = "https://docs.google.com/spreadsheets/d/1DrNVl-giSEDeDYRpCbiTrUOlVz_bh4fFm5wwsFYm24U/export?format=csv"
    # response = requests.get(gsheet_link_carbody)
    # data = response.content
    # df_carbody = pd.read_csv(BytesIO(data), encoding='utf-8')
    # df_carbody.to_csv('data/output_carbody.csv', index=False)

    return df_thirdparty
