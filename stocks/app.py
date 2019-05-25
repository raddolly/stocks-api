from flask import Flask
from nsetools import Nse
from datetime import date
from nsepy import get_history
import boto3
import pandas as pd
import threading


def main():
    # create_table()
    pull_data()
    return


def pull_data():
    stock_codes = nse.get_stock_codes(as_json=True)
    #print(stock_codes)
    codes = stock_codes.split('{')[1].split('}')[0].split(',')

    tr = {}
    for code in codes:
        tr[code] = threading.Thread(get_stock_quote(code))
        tr[code].start()

    for code in codes:
        tr[code].join()


def get_stock_quote(code):
    symbol = code.split(': ')[0].split('"')[1]

    if symbol == 'SYMBOL':
        return

    print(symbol)

    data = get_history(symbol=symbol, start=date(2019, 1, 1), end=date(2019, 4, 30))

    df = pd.DataFrame(data)
    for row_index, row in df.iterrows():
        record = str(row_index)
        for column in data.columns:
            record += ',' + str(row[column])
        key = str(row_index) + str(symbol)
        record += '\n'
        # print(record)
        push_to_kinesis(key, record)


def push_to_kinesis(key, content):
    kinesis_client.put_record(
        StreamName=kinesis_stream,
        Data=content,
        PartitionKey=key
    )


app = Flask(__name__)
nse = Nse()
kinesis_client = boto3.client('kinesis', region_name='us-east-1')
kinesis_stream = 'stocks-firehose'

main()