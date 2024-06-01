"""
This is a one-tine use script that loads part of the data in a CSV
file and inserts it into the database.
"""
import os
from datetime import date

import mysql.connector
import pandas as pd

with mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PWD"],
        database=os.environ["MYSQL_DB_NAME"],
    ) as db:
        with db.cursor() as c:
            current_date = date.today()

            df = pd.read_csv("./experiments/true_car_listings.csv").sample(n=300000)
            df = df[["State", "Make", "Model", "Year", "Mileage", "Price"]]
            df["State"] = df["State"].str.strip()
            df["Make"] = df["Make"].str.strip()
            df["Model"] = df["Model"].str.strip()
            df["current_date"] = current_date.strftime("%Y-%m-%d")
            rows = list(df.itertuples(index=False, name=None))
            rows=rows[:50000]
            values = ', '.join(map(str, rows))
            query = f"""INSERT INTO car_details (state, make, model, year, mileage, price, date_added) VALUES {values}"""
            print(query[:500])
            c.execute(query)
            db.commit()