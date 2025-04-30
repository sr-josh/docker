#!/usr/bin/env python
# coding: utf-8

import os
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine
# pd.__version__


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    csv_name = 'yellow.csv'

    os.system(f"wget {url} -O {csv_name}") #안 되면 curl -O {url}
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000, na_values='\\N')
    df = next(df_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    # df.passenger_count = df.passenger_count.replace(r'\\N', pd.NA, regex=True)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append') 

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            # df.passenger_count = df.passenger_count.replace(r'\\N', pd.NA, regex=True)
    
            df.to_sql(name=table_name, con=engine, if_exists='append') 
            t_end = time()
            print('insert... %.3f' % (t_end - t_start))
        except StopIteration:
            print("completed")
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postges')
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password name for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='db for postgres')
    parser.add_argument('--table_name', help='table name for postgres')
    parser.add_argument('--url', help='url for postgres')

    args = parser.parse_args()
    main(args)

    