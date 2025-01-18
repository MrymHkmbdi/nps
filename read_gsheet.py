import pandas as pd
import requests
from io import BytesIO

# gsheet_link  = "https://docs.google.com/spreadsheets/d/1WkC0A9qH6NikSwv0_HYv4l0EjIKwAb7PBjNEgDxnYcA/export?format=csv"
gsheet_link = "https://docs.google.com/spreadsheets/d/1WkC0A9qH6NikSwv0_HYv4l0EjIKwAb7PBjNEgDxnYcA/edit?usp=sharing"
response = requests.get(gsheet_link)
data = response.content

df = pd.read_csv(BytesIO(data), encoding='utf-8')
df.to_csv('data/output_thirdparty.csv', index=False)

gsheet_link = "https://docs.google.com/spreadsheets/d/1DrNVl-giSEDeDYRpCbiTrUOlVz_bh4fFm5wwsFYm24U/export?format=csv"

response = requests.get(gsheet_link)
data = response.content

df = pd.read_csv(BytesIO(data), encoding='utf-8')
df.to_csv('data/output_carbody.csv', index=False)