import os
import psycopg2
import bcrypt

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def create_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_table():
    """Create a user table, with ID, username, password, openai_key and port"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password BYTEA NOT NULL,
            openai_key VARCHAR(255) NOT NULL,
            port INTEGER
        )
    ''') # only create if the table does not exist yet
    conn.commit()
    conn.close()

def add_user(username, password, openai_key):
    """Add a user to the table"""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = %s', (username,)) # check if username already exists
    if cursor.fetchone() is not None:
        raise ValueError("Username already exists.")
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') # hashed passowrd
    port = 5001 + abs(hash(username)) % 1000 # add custom port in til 5999
    cursor.execute(
        'INSERT INTO users (username, password, openai_key, port) VALUES (%s, %s, %s, %s)', 
        (username, hashed_password, openai_key, port)
    )
    conn.commit()
    conn.close()

    
def verify_user(username, password):
    """Function to verify username and password with database"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = %s', (username,)) # get password
    result = cursor.fetchone()
    conn.close()

    if not result:
        return False # if not username

    # stored_hash: encode it to bytes before checking
    stored_hash = result[0].encode('utf-8') if isinstance(result[0], str) else bytes(result[0])
    
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash) # return true if password is correct

def get_user_info(username):
    """Get user info for startin user specific container hb_agent. Returns openai_key and port"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT openai_key, port FROM users WHERE username = %s', (username,)) # get username port and openai_key
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"openai_key": result[0], "port": result[1]} # return them
    else:
        return None