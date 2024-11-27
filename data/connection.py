import psycopg
import logging
from typing import Tuple, Union
import psycopg2
from datetime import datetime

# Async connection creation for psycopg3
async def get_db_connection():
    conn = await psycopg.AsyncConnection.connect(
        user="postgres",
        password="14489",
        # password="0549",
        host="localhost",
        port="5432",
        dbname="mydatabase"
    )
    
    # Set client encoding to UTF-8
    async with conn.cursor() as cursor:
        await cursor.execute("SET client_encoding TO 'UTF8'")
    
    return conn

def get_db_connection_sync():
    conn = psycopg2.connect(
        user="postgres",
        password="14489",
        # password="0549",
        host="localhost",
        port="5432",
        dbname="mydatabase"
    )
    
    # Set client encoding to UTF-8
    with conn.cursor() as cursor:
        cursor.execute("SET client_encoding TO 'UTF8'")
    
    return conn

async def insert_user_if_not_exists(user_id: int, user_name: str):
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            # Insert the user, or update the user_name if the user_id already exists
            await cur.execute(
                """
                INSERT INTO users (user_id, user_name)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET user_name = EXCLUDED.user_name;
                """,
                (user_id, user_name)
            )
            # Commit the transaction to make sure the insertion or update is saved
            await conn.commit()
            logging.info(f"User with ID {user_id} inserted or updated.")
    except Exception as e:
        logging.error(f"Error inserting or updating user: {e}")
    finally:
        # Ensure the connection is closed
        await conn.close()



async def check_file_exists(file_id: str, file_name: str) -> bool:
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            # Execute a query to check if the file_id exists in the input_file table
            await cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM input_file
                    WHERE file_id = %s OR file_name = %s
                );
                """,
                (file_id, file_name)
            )
            # Fetch the result
            result = await cur.fetchone()
            # Extract the boolean value from the result
            file_exists = result[0]
            return file_exists
    except Exception as e:
        logging.error(f"Error checking file existence: {e}")
        return False
    finally:
        # Ensure the connection is closed
        await conn.close()


async def get_message_id_by_id(record_id: int):
    conn = await get_db_connection()  # Assuming you have get_db_connection() defined
    try:
        async with conn.cursor() as cur:
            # Query to get the message_id by id
            await cur.execute(
                """
                SELECT message_id
                FROM output_file
                WHERE id = %s;
                """,
                (record_id,)
            )
            
            result = await cur.fetchone()  # Fetch one result
            if result:
                message_id = result[0]  # Extract message_id from the result tuple
                return message_id
            else:
                logging.info(f"No entry found for id: {record_id}")
                return None
    except Exception as e:
        logging.error(f"Error retrieving message_id: {e}")
        return None
    finally:
        # Ensure the connection is closed
        await conn.close()

async def get_id_by_message_id(record_id: int, vocal_percentage: int):
    conn = await get_db_connection()  # Assuming you have get_db_connection() defined
    try:
        async with conn.cursor() as cur:
            # Construct the table name dynamically based on vocal_percentage
            table_name = f"out_{vocal_percentage}"

            # Construct the SQL query dynamically
            query = f"""
                SELECT id
                FROM {table_name}
                WHERE message_id = %s;
            """

            # Execute the query
            await cur.execute(query, (record_id,))
            
            result = await cur.fetchone()  # Fetch one result
            if result:
                message_id = result[0]  # Extract message_id from the result tuple
                return message_id
            else:
                logging.info(f"No entry found for id: {record_id} in table: {table_name}")
                return None
    except Exception as e:
        logging.error(f"Error retrieving message_id from {table_name}: {e}")
        return None
    finally:
        # Ensure the connection is closed
        await conn.close()


async def link_exists(link: str) -> bool:
    conn = await get_db_connection()  # Assuming you have get_db_connection() defined
    try:
        async with conn.cursor() as cur:
            # Query to check if the link exists
            await cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM linksYou WHERE links = %s
                );
                """,
                (link,)  # Pass link as a tuple
            )
            # Fetch the result, which will be a single row with a single boolean value
            exists = await cur.fetchone()
            return exists[0]  # Return the boolean value
    except Exception as e:
        logging.error(f"Error checking link existence: {e}")
        return False  # Return False in case of error
    finally:
        await conn.close()  # Ensure the connection is closed


async def insert_into_input_file(file_id: str, file_name: str, file_name_original: str, duration: int):
    conn = await get_db_connection()  # Assuming you have get_db_connection() defined
    try:
        async with conn.cursor() as cur:
            # Insert into the input_file table
            await cur.execute(
                """
                INSERT INTO input_file (file_id, file_name, file_name_original, duration)
                VALUES (%s, %s, %s, %s);
                """,
                (file_id, file_name, file_name_original, duration)
            )
            await conn.commit()  # Commit the transaction to save the data
            logging.info(f"Inserted into input_file: file_id={file_id}")
    except Exception as e:
        logging.error(f"Error inserting into input_file: {e}")
    finally:
        await conn.close()  # Ensure the connection is closed


async def check_file_exists_with_percentage(file_id: str, file_name: str, percent: int, check_value: str = "not_zero") -> bool:
    """
    Check if a file exists in the database with a specific percentage condition.

    Args:
        file_id (str): The file ID to check.
        percent (int): The percentage column to check (e.g., `out_{percent}_id`).
        check_value (str): The condition to check ('negative_one' or 'not_zero').

    Returns:
        bool: True if the condition is met, False otherwise.
    """
    conn = await get_db_connection()
    try:
        # Dynamically create the column name based on the percentage
        column_name = f"out_{percent}_id"

        # Determine the condition based on check_value
        if check_value == "negative_one":
            condition = f"{column_name} = -1"
        elif check_value == "not_zero":
            condition = f"{column_name} != 0"
        else:
            raise ValueError("Invalid check_value. Use 'negative_one' or 'not_zero'.")

        async with conn.cursor() as cur:
            # Execute a query to check the condition
            query = f"""
                SELECT EXISTS (
                    SELECT 1
                    FROM input_file
                    WHERE (file_id = %s OR file_name = %s) AND {condition}
                );
            """
            await cur.execute(query, (file_id, file_name))
            
            # Fetch the result
            result = await cur.fetchone()

            # Extract the boolean value from the result
            return result[0]
    except Exception as e:
        logging.error(f"Error checking file existence with {percent}% ({check_value}): {e}")
        return False
    finally:
        # Ensure the connection is closed
        await conn.close()



async def get_output_id_for_percentage(file_id: str, percent: int) -> int:
    conn = await get_db_connection()
    try:
        # Dynamically create the column name based on the percentage
        column_name = f"out_{percent}_id"

        async with conn.cursor() as cur:
            # Execute a query to fetch the value of out_{percent}_id for the given file_id
            query = f"""
                SELECT {column_name}
                FROM input_file
                WHERE file_id = %s;
            """
            await cur.execute(query, (file_id,))
            
            # Fetch the result
            result = await cur.fetchone()

            # Extract and return the value from the result, or return 0 if the column is null
            return result[0] if result else 0
    except Exception as e:
        logging.error(f"Error fetching output ID for {percent}%: {e}")
        return 0  # Return 0 in case of any error
    finally:
        # Ensure the connection is closed
        await conn.close()


async def get_chat_and_message_id_by_id(id: int, percentage: int):
    table_name = f"out_{percentage}"  # Dynamic table name based on percentage
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            # Query to retrieve chat_id and message_id based on the given id
            query = f"""
                SELECT chat_id, message_id
                FROM {table_name}
                WHERE id = %s;
            """
            await cur.execute(query, (id,))
            result = await cur.fetchone()

            if result:
                chat_id, message_id = result
                return chat_id, message_id
            else:
                logging.info(f"No record found in {table_name} with id {id}.")
                return None, None
    except Exception as e:
        logging.error(f"Error retrieving chat_id and message_id from {table_name}: {e}")
        return None, None
    finally:
        await conn.close()

import logging

async def get_name_by_id(file_id: str) -> str:
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            # Execute a query to fetch the file_name for the given file_id
            query = """
                SELECT file_name
                FROM input_file
                WHERE file_id = %s;
            """
            await cur.execute(query, (file_id,))
            
            # Fetch the result
            result = await cur.fetchone()

            # Return the file_name if found, or None if not found
            return result[0] if result else None
    except Exception as e:
        logging.error(f"Error fetching file_name for file_id {file_id}: {e}")
        return None  # Return None in case of any error
    finally:
        # Ensure the connection is closed
        await conn.close()

def get_name_by_songId(id: int) -> str:
    conn = get_db_connection_sync()
    try:
        with conn.cursor() as cur:
            # Execute a query to fetch the file_name for the given file_id
            query = """
                SELECT file_name, file_name_original
                FROM input_file
                WHERE id = %s;
            """
            cur.execute(query, (id,))
            
            # Fetch the result
            result = cur.fetchone()

            # Return the file_name if found, or None if not found
            return result if result else None
    except Exception as e:
        logging.error(f"Error fetching file_name for file_id {id}: {e}")
        return None  # Return None in case of any error
    finally:
        # Ensure the connection is closed
        conn.close()

async def insert_chat_and_message_id(chat_id: int, message_id: int, percentage: int):
    """
    Inserts chat_id and message_id into the dynamically selected table based on percentage 
    and returns the id of the newly inserted row.
    """
    table_name = f"out_{percentage}"  # Dynamic table name based on percentage
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            # Query to insert chat_id and message_id and return the id of the inserted row
            query = f"""
                INSERT INTO {table_name} (chat_id, message_id)
                VALUES (%s, %s)
                RETURNING id;
            """
            await cur.execute(query, (chat_id, message_id))
            result = await cur.fetchone()  # Fetch the returning id
            inserted_id = result[0] if result else None
            await conn.commit()  # Commit the transaction
            logging.info(f"Successfully inserted into {table_name} with chat_id {chat_id} and message_id {message_id}.")
            return inserted_id
    except Exception as e:
        logging.error(f"Error inserting into {table_name}: {e}")
        return None
    finally:
        await conn.close()



async def update_out_id_by_percent(file_id: str, out_id: int, percent: int):
    connection = await get_db_connection()
    out_column = f"out_{percent}_id"
    try:
        # Establish the async connection to the database
        connection = await get_db_connection()

        # Use async context manager with the connection cursor
        async with connection.cursor() as cursor:
            # Define the SQL command to update the language_id
            query = f"""
                UPDATE input_file
                SET {out_column} = %s
                WHERE file_id = %s;
            """
            
            # Execute the SQL command with parameters
            await cursor.execute(query, (out_id, file_id))
            
            # Commit the transaction
            await connection.commit()
            print("Successfully updated {out_column} for file_id {file_id} value {out_id}.")

    except (Exception, psycopg.Error) as error:
        print("Error while updating:", error)
    
    finally:
        if connection:
            await connection.close()
            print("PostgreSQL connection is closed")

async def get_id_by_file_id(file_id: str):
    """
    Retrieves the id from the table based on the given file_id.

    :param file_id: The file identifier to search for.
    :return: The id associated with the given file_id, or None if not found.
    """
    query = """
        SELECT id
        FROM input_file
        WHERE file_id = %s;
    """
    
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query, (file_id,))
            result = await cur.fetchone()  # Fetch the first matching result
            
            if result:
                return result[0]  # Return the id
            else:
                logging.info(f"No record found for file_id: {file_id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving id for file_id {file_id}: {e}")
        return None
    finally:
        await conn.close()

async def get_file_id_by_id(id: int):
    """
    Retrieves the file_id from the table based on the given id.

    :param id: The identifier to search for.
    :return: The file_id associated with the given id, or None if not found.
    """
    query = """
        SELECT file_id
        FROM input_file
        WHERE id = %s;
    """
    
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query, (id,))
            result = await cur.fetchone()  # Fetch the first matching result
            
            if result:
                return result[0]  # Return the file_id
            else:
                logging.info(f"No record found for id: {id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving file_id for id {id}: {e}")
        return None
    finally:
        await conn.close()
        
async def get_duration_by_id_links(id: int):
    """
    Retrieves the file_id from the table based on the given id.

    :param id: The identifier to search for.
    :return: The file_id associated with the given id, or None if not found.
    """
    query = """
        SELECT duration
        FROM linksyou
        WHERE id = %s;
    """
    
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query, (id,))
            result = await cur.fetchone()  # Fetch the first matching result
            
            if result:
                return result[0]  # Return the file_id
            else:
                logging.info(f"No record found for id: {id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving file_id for id {id}: {e}")
        return None
    finally:
        await conn.close()


async def update_order_list_true(id: int):
    connection = None
    try:
        # Establish the connection to the database asynchronously
        connection = await get_db_connection()
        
        # Define the SQL query to update the status to TRUE
        query = """
            UPDATE order_list
            SET status = TRUE
            WHERE url_id = $1;
        """
        
        # Use an async cursor to execute the query
        async with connection.cursor() as cursor:
            await cursor.execute(query, (id,))
        
        # Commit the transaction to save the changes
        await connection.commit()
        
        # Log success message
        logging.info(f"Successfully updated order_list for id {id} to TRUE.")
    
    except (Exception, psycopg.Error) as error:
        logging.error(f"Error while updating order_list: {error}", exc_info=True)
    
    finally:
        if connection:
            await connection.close()
            logging.info("PostgreSQL connection is closed.")


async def get_duration_by_id(id: int):
    """
    Retrieves the file_id from the table based on the given id.

    :param id: The identifier to search for.
    :return: The file_id associated with the given id, or None if not found.
    """
    query = """
        SELECT duration
        FROM input_file
        WHERE id = %s;
    """
    
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query, (id,))
            result = await cur.fetchone()  # Fetch the first matching result
            
            if result:
                return result[0]  # Return the file_id
            else:
                logging.info(f"No record found for id: {id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving file_id for id {id}: {e}")
        return None
    finally:
        await conn.close()







async def get_file_name_original_by_id(id: int):
    """
    Retrieves the file_name_original from the table based on the given id.

    :param id: The identifier to search for.
    :return: The file_name_original associated with the given id, or None if not found.
    """
    query = """
        SELECT file_name_original
        FROM input_file
        WHERE id = %s;
    """
    
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query, (id,))
            result = await cur.fetchone()  # Fetch the first matching result
            
            if result:
                return result[0]  # Return the file_name_original
            else:
                logging.info(f"No record found for id: {id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving file_name_original for id {id}: {e}")
        return None
    finally:
        await conn.close()

def get_file_id_by_id_sync(id: int):
    """
    Retrieves the file_name from the table based on the given id.

    :param id: The identifier to search for.
    :return: The file_name associated with the given id, or None if not found.
    """
    query = """
        SELECT file_id
        FROM input_file
        WHERE id = %s;
    """
    
    conn = get_db_connection_sync()  # Synchronous connection to the database
    try:
        with conn.cursor() as cur:
            logging.info(f"Executing query: {query} with id: {id}")
            cur.execute(query, (id,))
            result = cur.fetchone()  # Fetch the first matching result
            
            if result:
                logging.info(f"Record found for id {id}: {result[0]}")
                return result[0]  # Return the file_name
            else:
                logging.info(f"No record found for id: {id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving file_name for id {id}: {e}")
        return None
    finally:
        conn.close()  # Ensure the connection is closed

async def get_file_name_by_id(id: int):
    """
    Retrieves the file_name from the table based on the given id.

    :param id: The identifier to search for.
    :return: The file_name associated with the given id, or None if not found.
    """
    query = """
        SELECT file_name
        FROM input_file
        WHERE id = %s;
    """
    
    conn = await get_db_connection()  # Asynchronous connection to the database
    try:
        async with conn.cursor() as cur:
            logging.info(f"Executing query: {query} with id: {id}")
            await cur.execute(query, (id,))
            result = await cur.fetchone()  # Fetch the first matching result
            
            if result:
                logging.info(f"Record found for id {id}: {result[0]}")
                return result[0]  # Return the file_name
            else:
                logging.info(f"No record found for id: {id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving file_name for id {id}: {e}")
        return None
    finally:
        await conn.close()  # Ensure the connection is closed asynchronously


async def get_user_ids():
    """
    Retrieves the full list of user_ids from the 'users' table.

    :return: A list of all user_ids or an empty list if no users are found.
    """
    query = """
        SELECT user_id
        FROM users WHERE status = 'ordinary';
    """
    
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchall()  # Fetch all matching results
            
            if result:
                # Extract user_id from each row and return as a list
                user_ids = [row[0] for row in result]
                return user_ids
            else:
                logging.info("No users found in the table.")
                return []
    except Exception as e:
        logging.error(f"Error retrieving user_ids: {e}")
        return []
    finally:
        await conn.close()

async def get_user_ids_all():
    """
    Retrieves the full list of user_ids from the 'users' table.

    :return: A list of all user_ids or an empty list if no users are found.
    """
    query = """
        SELECT user_id
        FROM users;
    """
    
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchall()  # Fetch all matching results
            
            if result:
                # Extract user_id from each row and return as a list
                user_ids = [row[0] for row in result]
                return user_ids
            else:
                logging.info("No users found in the table.")
                return []
    except Exception as e:
        logging.error(f"Error retrieving user_ids: {e}")
        return []
    finally:
        await conn.close()


async def insert_links(url: str, user_id : int):
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            # Insert the user, or update the user_name if the user_id already exists
            await cur.execute(
                "SELECT 1 FROM linksYou WHERE links = %s LIMIT 1",
                (url,)
            )
            exists = await cur.fetchone()
            
            # If the link does not exist, insert the data
            if not exists:
                await cur.execute(
                    """
                    INSERT INTO linksYou (links, chatid)
                    VALUES (%s, %s)
                    """,
                    (url, user_id)
                )
                await conn.commit()
            logging.info(f"Inserted data to url {url} \n data to user {user_id}")
    except Exception as e:
        logging.error(f"Error inserting or updating user: {e}")
    finally:
        # Ensure the connection is closed
        await conn.close()


async def get_link_duration(link: str):
    conn = await get_db_connection()  # Assuming you have get_db_connection() defined
    try:
        async with conn.cursor() as cur:
            # Query to get the duration if the link exists
            await cur.execute(
                """
                SELECT duration FROM linksYou WHERE links = %s;
                """,
                (link,)  # Pass link as a tuple
            )
            # Fetch the result, which will be a single row if the link exists
            result = await cur.fetchone()
            return result[0] if result else None  # Return duration if found, else None
    except Exception as e:
        logging.error(f"Error retrieving link duration: {e}")
        return None  # Return None in case of error
    finally:
        await conn.close()


async def get_link_data(link: str) -> Union[Tuple[int, int], None]:
    conn = await get_db_connection()  # Assuming you have get_db_connection() defined
    try:
        async with conn.cursor() as cur:
            # Query to get chat_id and message_id if the link exists
            await cur.execute(
                """
                SELECT chatid, messageid FROM linksYou WHERE links = %s;
                """,
                (link,)  # Pass link as a tuple
            )
            # Fetch the result, which will be a single row if the link exists
            result = await cur.fetchone()
            return (result[0], result[1]) if result else None  # Return chat_id and message_id if found, else None
    except Exception as e:
        logging.error(f"Error retrieving link data: {e}")
        return None  # Return None in case of error
    finally:
        await conn.close()


async def get_id_byUrl(link: str) -> Union[Tuple[int, int], None]:
    conn = await get_db_connection()  # Assuming you have get_db_connection() defined
    try:
        async with conn.cursor() as cur:
            # Query to get chat_id and message_id if the link exists
            await cur.execute(
                """
                SELECT id FROM linksYou WHERE links = %s;
                """,
                (link,)  # Pass link as a tuple
            )
            # Fetch the result, which will be a single row if the link exists
            result = await cur.fetchone()
            return result[0] if result else None  # Return chat_id and message_id if found, else None
    except Exception as e:
        logging.error(f"Error retrieving link data: {e}")
        return None  # Return None in case of error
    finally:
        await conn.close()

async def check_file_exists_order_true(url_id: str) -> bool:
    conn = await get_db_connection()  # Assuming this function returns an async database connection
    try:
        async with conn.cursor() as cur:
            # Query to check if a file with url_id exists in order_list and has status = TRUE
            await cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM order_list
                    WHERE url_id = %s AND status = TRUE
                );
                """,
                (url_id,)
            )
            # Fetch the result and extract the boolean value
            result = await cur.fetchone()
            return result[0] if result else False
    except Exception as e:
        logging.error(f"Error checking file existence for url_id {url_id}: {e}")
        return False
    finally:
        await conn.close()  # Ensure the connection is closed

async def check_file_exists_order(url_id: str) -> bool:
    conn = await get_db_connection()  # Assuming this function returns an async database connection
    try:
        async with conn.cursor() as cur:
            # Query to check if a file with url_id exists in order_list and has status = TRUE
            await cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM order_list
                    WHERE url_id = %s
                );
                """,
                (url_id,)
            )
            # Fetch the result and extract the boolean value
            result = await cur.fetchone()
            return result[0] if result else False
    except Exception as e:
        logging.error(f"Error checking file existence for url_id {url_id}: {e}")
        return False
    finally:
        await conn.close()  # Ensure the connection is closed


async def get_chat_idBy_id(song_id: int):
    """
    Retrieves the id from the table based on the given file_id.

    :param file_id: The file identifier to search for.
    :return: The id associated with the given file_id, or None if not found.
    """
    query = """
        SELECT chatid
        FROM linksyou
        WHERE id = %s;
    """
    
    conn = await get_db_connection()  # Assuming you have an async function to get DB connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query, (song_id,))
            result = await cur.fetchone()  # Fetch the first matching result
            
            if result:
                return result[0]  # Return the id
            else:
                logging.info(f"No record found for file_id: {song_id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving id for file_id {song_id}: {e}")
        return None
    finally:
        await conn.close()




async def update_linksYou_message_id(id: int, message_id: int):
    """
    Updates the message_id for a specific link in the `linksyou` table.

    Args:
        id (int): The ID of the link to update.
        message_id (int): The new message_id value.
    """
    try:
        # Establish an async connection to the database
        connection = await get_db_connection()

        # Use an async context manager with the connection cursor
        async with connection.cursor() as cursor:
            query = """
                UPDATE linksyou
                SET messageid = %s
                WHERE id = %s;
            """
            # Execute the SQL command with parameters
            await cursor.execute(query, (message_id, id))
            await connection.commit()  # Commit the transaction
            logging.info(f"Successfully updated message_id for id '{id}' to '{message_id}'.")
    except (Exception, psycopg.DatabaseError) as error:
        logging.error(f"Error while updating message_id for id '{id}': {error}")
    finally:
        if connection:
            await connection.close()
            logging.info("PostgreSQL connection is closed.")
            print("PostgreSQL connection is closed")


async def update_links_duration(links: str, duration: int):
    """
    Updates the duration for a specific link in the `linksyou` table.

    Args:
        links (str): The link to update.
        duration (int): The new duration value.
    """
    try:
        # Establish an async connection to the database
        connection = await get_db_connection()

        # Use an async cursor to execute the query
        async with connection.cursor() as cursor:
            query = """
                UPDATE linksyou
                SET duration = %s
                WHERE links = %s;
            """
            await cursor.execute(query, (duration, links))
            await connection.commit()  # Commit the transaction
            logging.info(f"Successfully updated duration for link '{links}' to {duration}.")
    except (Exception, psycopg.DatabaseError) as error:
        logging.error(f"Error while updating duration for link '{links}': {error}")
    finally:
        if connection:
            await connection.close()
            logging.info("PostgreSQL connection is closed.")


async def check_user_premium(user_id) -> bool:
    conn = await get_db_connection()  # Assuming this function returns an async database connection
    try:
        async with conn.cursor() as cur:
            # Query to check if a file with url_id exists in order_list and has status = TRUE
            await cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM users
                    WHERE user_id = %s AND status = TRUE
                );
                """,
                (user_id,)
            )
            # Fetch the result and extract the boolean value
            result = await cur.fetchone()
            return result[0] if result else False
    except Exception as e:
        logging.error(f"Error checking file existence for url_id {user_id}: {e}")
        return False
    finally:
        await conn.close()  # Ensure the connection is closed



async def check_and_update_premium_status() -> None:
    """
    Check the `deadline_at` column and downgrade expired premium users to ordinary.
    """
    current_date = datetime.now()
    query_select = """
    SELECT user_id, deadline_at
    FROM users
    WHERE status = TRUE;
    """
    query_update = """
    UPDATE users
    SET status = FALSE
    WHERE user_id = %s;
    """
    
    conn = await get_db_connection()  # Get the async database connection
    try:
        async with conn.cursor() as cur:
            # Fetch all premium users
            await cur.execute(query_select)
            users = await cur.fetchall()

            # Check and update the status of each user
            for user_id, deadline_at in users:
                if deadline_at and deadline_at < current_date:
                    # Downgrade to ordinary if the premium period has expired
                    await cur.execute(query_update, (user_id,))
                    logging.info(f"User {user_id} downgraded to ordinary.")
            
            # Commit changes to the database
            await conn.commit()
    except Exception as e:
        logging.error(f"Error while checking/updating premium status: {e}")
    finally:
        # Ensure the connection is closed
        await conn.close()


def get_url_By_id(song_id: int):
    """
    Retrieves the URL from the table based on the given song_id.

    :param song_id: The song identifier to search for.
    :return: The URL associated with the given song_id, or None if not found.
    """
    query = """
        SELECT links
        FROM linksyou
        WHERE id = %s;
    """
    
    try:
        # Establish a synchronous database connection
        conn = get_db_connection_sync()
        with conn.cursor() as cur:
            cur.execute(query, (song_id,))
            result = cur.fetchone()  # Fetch the first matching result
            
            if result:
                return result[0]  # Return the URL
            else:
                logging.info(f"No record found for song_id: {song_id}.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving URL for song_id {song_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()  # Ensure the connection is closed




async def insert_into_order_list(url_id: int):
    conn = await get_db_connection()  # Assuming you have get_db_connection() defined
    try:
        async with conn.cursor() as cur:
            # Insert into the input_file table
            await cur.execute(
                """
                INSERT INTO order_list (url_id)
                VALUES (%s);
                """,
                (url_id,)
            )
            await conn.commit()  # Commit the transaction to save the data
            logging.info(f"Inserted into order_list: url_id={url_id}")
    except Exception as e:
        logging.error(f"Error inserting into order_list: {e}")
    finally:
        await conn.close()  # Ensure the connection is closed


def get_url_ids_status_true():
    """
    Retrieves the list of url_ids from the 'order_list' table where status is TRUE.

    :return: A list of url_ids or an empty list if no matches are found.
    """
    query = """
        SELECT url_id
        FROM order_list
        WHERE status = TRUE;
    """

    connection = None
    try:
        # Establish a connection to the database
        connection = get_db_connection_sync()
        
        # Use a context manager to handle the cursor
        with connection.cursor() as cursor:
            # Execute the query
            cursor.execute(query)
            # Fetch all matching rows
            result = cursor.fetchall()
            # Extract url_id from each row and return as a list
            url_ids = [row[0] for row in result]
            return url_ids
    except Exception as e:
        logging.error(f"Error retrieving url_ids: {e}", exc_info=True)
        return []
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed.")

# async def get_url_ids_status_true():
#     """
#     Retrieves the list of url_ids from the 'order_list' table where status is TRUE.

#     :return: A list of url_ids or an empty list if no matches are found.
#     """
#     query = """
#         SELECT url_id
#         FROM order_list
#         WHERE status = TRUE;
#     """

#     conn = await get_db_connection()  # Your async function to get the psycopg3 connection
#     try:
#         async with conn.cursor() as cur:
#             await cur.execute(query)
#             result = await cur.fetchall()  # Fetch all matching rows
#             # Extract url_id from each row and return as a list
#             url_ids = [row[0] for row in result]
#             return url_ids
#     except Exception as e:
#         logging.error(f"Error retrieving url_ids: {e}")
#         return []
#     finally:
#         await conn.close()


async def get_url_duration_0():
    """
    Retrieves the list of url_ids from the 'order_list' table where status is TRUE.

    :return: A list of url_ids or an empty list if no matches are found.
    """
    query = """
        SELECT links
        FROM linksyou
        WHERE duration = 0;
    """

    conn = await get_db_connection()  # Your async function to get the psycopg3 connection
    try:
        async with conn.cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchall()  # Fetch all matching rows
            # Extract url_id from each row and return as a list
            url_ids = [row[0] for row in result]
            return url_ids
    except Exception as e:
        logging.error(f"Error retrieving url_ids: {e}")
        return []
    finally:
        await conn.close()



def update_order_list_false(id: int):
    connection = None
    try:
        # Establish the connection to the database
        connection = get_db_connection_sync()
        
        # Create a cursor to perform database operations
        with connection.cursor() as cursor:
            # Define the SQL query to update the status to FALSE
            query = """
                UPDATE order_list
                SET status = FALSE
                WHERE url_id = %s;
            """
            
            # Execute the query with the provided id
            cursor.execute(query, (id,))
            
            # Commit the transaction to save the changes
            connection.commit()
            logging.info(f"Successfully updated order_list for id {id} to FALSE.")

    except (Exception, psycopg2.Error) as error:
        logging.error(f"Error while updating order_list: {error}", exc_info=True)
    
    finally:
        if connection:
            connection.close()
            logging.info("PostgreSQL connection is closed.")

# async def update_order_list_false(id: int):
#     connection = None
#     try:
#         # Establish the async connection to the database
#         connection = await get_db_connection()

#         # Use async context manager with the connection cursor
#         async with connection.cursor() as cursor:
#             # Define the SQL command to update the status to FALSE
#             query = """
#                 UPDATE order_list
#                 SET status = FALSE
#                 WHERE url_id = %s;
#             """
            
#             # Execute the SQL command with parameters
#             await cursor.execute(query, (id,))  # Pass parameters as a tuple
            
#             # Commit the transaction
#             await connection.commit()
#             logging.info(f"Successfully updated order_list for id {id} to FALSE.")

#     except (Exception, psycopg.Error) as error:
#         logging.error(f"Error while updating order_list: {error}", exc_info=True)
    
#     finally:
#         if connection:
#             await connection.close()
#             logging.info("PostgreSQL connection is closed.")