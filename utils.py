import snowflake.connector
import pandas as pd


def get_snowflake_data(query: str, schema: str):
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user='SHAZIAANWER',
        password='ShaziaAnwer123',
        account='qxqpfvm-xl67344',
        warehouse='COMPUTE_WH',
        database='BHARATVERSE_DB',
        schema=schema
    )

    # Execute the query and fetch data
    cur = conn.cursor()
    cur.execute(query)
    data = cur.fetch_pandas_all()  # Fetch the data into a Pandas DataFrame
    conn.close()  # Close the connection

    # Clean the column names
    data.columns = [col.strip().lower() for col in data.columns]
    
    return data


def load_art_data_snowflake():
    query = "SELECT State, ArtForm, Category, Description,image_url FROM ART_FORMS"
    return get_snowflake_data(query, "ARTFORM_DATA")


def load_tourism_data_snowflake():
    query = "SELECT State, DomesticVisitors, ForeignVisitors FROM TOURISM_STATS"
    return get_snowflake_data(query, "TOURISM_DATA")


def load_seasonal_data_snowflake():
    query = "SELECT State, Month, Visitors FROM SEASONAL_TREND"
    return get_snowflake_data(query, "SEASONAL_DATA")


def get_best_months(state, seasonal_df):
    seasonal_df = seasonal_df.copy()
    seasonal_df["state"] = seasonal_df["state"].str.strip().str.lower()
    state = state.strip().lower()

    state_data = seasonal_df[seasonal_df["state"] == state]

    if not state_data.empty:
        top_months = state_data.sort_values(by="visitors", ascending=False).head(3)
        return list(top_months["month"])
    return ["Data not available"]
