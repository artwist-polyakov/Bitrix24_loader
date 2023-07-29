import clickhouse_connect
from tqdm import tqdm
import time

def get_client(host, port, user, password, db_name, https = True):
    return clickhouse_connect.get_client(interface = 'https' if https else 'http', host=host, port=port, username=user, password=password, database=db_name)


def test_connection(host, port, user, password, db_name):
    client = get_client(host, port, user, password, db_name)
    try: 
        client.command('SELECT 1')
        print("Successfully connected to the database.")
    except:
        print("Failed to connect to the database.")
    # tables = client.command(f'SELECT name FROM system.tables')
    # print(tables)
    # for i in tables.split('\n'):
    #     print(i+':')
    #     print(client.command(f"SELECT engine FROM system.tables WHERE name = '{i}'"))

def check_tabletype_errors(table, host, port, user, password, db_name):
    client = get_client(host, port, user, password, db_name)
    message = f"Table {table} is not MergeTree engine. Please use MergeTree engine."
    return client.command(f"SELECT engine FROM system.tables WHERE name = '{table}'").split('\n') != "MergeTree", message

def get_columns_and_types(table, host, port, user, password, db_name):
    client = get_client(host, port, user, password, db_name)
    response = client.command(f'DESCRIBE TABLE {table}')
    # print(response)
    result = terrible_list_to_dict(response)
    # for line in response:
    #     print(line)
        # record = {}
        # if line:
        #     record['name'] = line.split('\t')[0]
        #     record['type'] = line.split('\t')[1]
        #     result.append(record)
    # columns = [{'name':line.split('\t')[0], 'type':line.split('\t')[1]} for line in response if line]
    # columns = [line.split('\t') for line in response.split('\n') if line]
    return result

def load_data_to_sql(data, table, fields_matching, host, port, user, password, db_name):
    client = get_client(host, port, user, password, db_name)
    total = len(data)
    progress_bar = tqdm(total=total, position=0, leave=True)
    k = 0

    for row in data:
        row = {fields_matching.get(key, key): value for key, value in row.items()}
        ID = row.get('ID')  # assuming 'id' is the key for the unique identifier

        # Check if there's a record with this id in the table and the sum of 'sign' for each 'version' equals 1
        response = client.command(f"SELECT version, SUM(sign) as sum_sign FROM {table} WHERE ID = {ID} GROUP BY version HAVING sum_sign = 1")
        print(response)
        versions = [row.split('\t')[0] for row in response.split('\n') if row]

        # For each version, create a copy with sign=-1 and insert it into the table
        for version in versions:
            negative_row = row.copy()
            negative_row['version'] = version
            negative_row['sign'] = -1
            client.insert(table, [list(negative_row.values())], column_names=list(negative_row.keys()))

        # Insert the new data with sign=1 and version as the current timestamp
        row['version'] = int(time.time())  # current timestamp
        row['sign'] = 1
        client.insert(table, [list(row.values())], column_names=list(row.keys()))

        k += 1
        if k % 100 == 0:
            progress_bar.update(100)

    progress_bar.close()

def terrible_list_to_dict(data):
    result = []
    key = None

    for item in data:
        if item:  # if the item is not empty
            if item.startswith('\n') or key is None:  # if it is a field name or the first non-empty string
                key = item.strip()
            elif key:  # if it is a field type and we have a key
                result.append({'name': key, 'type': item.strip(), 'nullable': False})
                key = None  # reset the key
    return result
