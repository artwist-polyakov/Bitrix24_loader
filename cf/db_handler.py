from sqlalchemy import create_engine, inspect, text
import pymysql
from tqdm import tqdm

def get_columns_and_types(table, host, port, user, password, db_name):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}") 
    inspector = inspect(engine)
    columns = inspector.get_columns(table)
    return columns

def check_tabletype_errors(table, host, port, user, password, db_name):
    return False, ""


def test_connection(host, port, user, password, db_name):
    print(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")
    try:
        # Создаем движок SQLAlchemy
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}") 
        # Выполняем простой SQL-запрос
        result = engine.execute("SELECT 1")
        # Если запрос выполнен успешно, выводим сообщение об успешном подключении
        print("Successfully connected to the database.")
    except Exception as e:
        # Если при выполнении запроса возникла ошибка, выводим сообщение об ошибке
        print("Failed to connect to the database.")
        print(str(e))

def get_columns_and_types_sql(table, host, port, user, password, db_name):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}") 
    inspector = inspect(engine)
    columns = inspector.get_columns(table)
    # print(columns)
    return columns

def test_connection(host, port, user, password, db_name):
    try:
        # Создаем движок SQLAlchemy
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}") 
        # Выполняем простой SQL-запрос
        result = engine.execute("SELECT 1")
        # Если запрос выполнен успешно, выводим сообщение об успешном подключении
        print("Successfully connected to the database.")
    except Exception as e:
        # Если при выполнении запроса возникла ошибка, выводим сообщение об ошибке
        print("Failed to connect to the database.")
        print(str(e))

def load_data_to_sql(data, table, fields_matching, host, port, user, password, db_name, relaxing = False):
    # Создаем движок SQLAlchemy
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}") 
    total = len(data)
    progress_bar = tqdm(total=total, position=0, leave=True)
    k = 0
    # Начинаем транзакцию
    with engine.begin() as connection:
        for row in data:
            row = {fields_matching.get(key, key): value for key, value in row.items()}
            # Форматируем SQL запрос
            sql = text(f"""
            INSERT INTO {table} ({','.join(row.keys())}) VALUES ({','.join(':' + key for key in row.keys())})
            ON DUPLICATE KEY UPDATE 
            {', '.join(f'{key} = VALUES({key})' for key in row.keys())}
            """)
            # Выполняем SQL запрос
            connection.execute(sql, **row)
            k+=1
            if k % 100 == 0:
                progress_bar.update(100)

def delete_by_id(id, table, host, port, user, password, db_name):
    # Создаем движок SQLAlchemy
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")
    # Начинаем транзакцию
    with engine.begin() as connection:
        # Форматируем SQL запрос
        sql = text(f"DELETE FROM {table} WHERE ID = :id")
        # Выполняем SQL запрос
        connection.execute(sql, id=id)
