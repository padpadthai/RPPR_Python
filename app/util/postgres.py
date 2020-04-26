import logging
from typing import List

from psycopg2 import sql, Error as PostgresError, DatabaseError
from psycopg2.extensions import AsIs
from psycopg2.extras import execute_values


def create_table(connection, name: str, metadata: List[str]):
    command = "CREATE TABLE IF NOT EXISTS %s (%s)"  # requires PostgreSQL >= 9.1
    metadata_joined = ', '.join(metadata)
    run_command(connection, command, [AsIs(name), AsIs(metadata_joined)],
                "There was a problem creating the table '{}'".format(name))


def drop_table(connection, name: str):
    command = "DROP TABLE IF EXISTS %s"
    run_command(connection, command, [AsIs(name)],
                "There was a problem dropping the table '{}'".format(name))


def read_all(connection, table_name: str):
    command = "SELECT * FROM %s"
    with connection, connection.cursor() as cursor:
        try:
            cursor.execute(command, [AsIs(table_name)])
            return cursor.fetchall()
        except PostgresError:
            logging.error("There was a problem reading data from '{}'".format(table_name))
            raise


def bulk_insert(connection, table_name: str, columns: List[str], values):
    columns_joined = sql.SQL(', ').join(map(sql.Identifier, columns))
    command = sql.SQL("INSERT INTO {}({}) VALUES %s") \
        .format(sql.Identifier(table_name), columns_joined)
    with connection, connection.cursor() as cursor:
        try:
            execute_values(cursor, command, values, page_size=1000)
        except DatabaseError as error:
            logging.error("There was a problem persisting property sales '{}'", error.pgerror)
            raise


def run_command(connection, command: str, arguments: List,
                error_message="There was a problem performing this operation"):
    with connection, connection.cursor() as cursor:
        try:
            cursor.execute(command, arguments)
        except PostgresError:
            logging.error(error_message)
            logging.debug("Last command run: {}".format(cursor.mogrify(command, arguments)))
            raise
