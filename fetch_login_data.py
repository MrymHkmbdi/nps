import requests
import pandas as pd

username = "m.hokmabadi@bimebazar.com"
password = "CEme12031399"

sql_query = """
WITH T AS (
    SELECT
        created_date::DATE AS attempts_date,
        SUM(CASE WHEN logged_in_on IS NOT NULL THEN 1 ELSE 0 END) AS successful_attempts
    FROM 
        users_otploginlog
    WHERE 
        (SOURCE IS NULL OR SOURCE NOT LIKE '%partner%')
    GROUP BY 
        created_date::DATE, username
)
SELECT 
    COUNT(*) as counter,
    attempts_date AS attempts_week_start,
    SUM(CASE WHEN successful_attempts >= 1 THEN 1 ELSE 0 END) AS success_count
FROM 
    T
GROUP BY 
    attempts_date
ORDER BY 
    attempts_date;
"""


def fetch_login_data():
    response = requests.post(
        "https://bijik.bimebazar.com/api/session",
        json={"username": "m.hokmabadi@bimebazar.com", "password": "CEme12031399"}
    )
    if response.status_code != 200:
        raise Exception(f"Failed to log in to Metabase: {response.text}")
    token = response.json()["id"]

    # Run SQL query
    headers = {"X-Metabase-Session": token}
    payload = {
        "type": "native",
        # "native": {"query": sql_query.format(start_date=start_date, end_date=end_date)},
        "native": {"query": sql_query},
        "database": 2
    }
    response = requests.post(
        "https://bijik.bimebazar.com/api/dataset",
        headers=headers,
        json=payload
    )
    if not response.ok:
        raise Exception(f"Failed to run SQL query: {response.text}")

    # Convert results to DataFrame
    rows = response.json().get("data", {}).get("rows", [])
    cols = [col["display_name"] for col in response.json().get("data", {}).get("cols", [])]
    df = pd.DataFrame(rows, columns=cols)

    return df
