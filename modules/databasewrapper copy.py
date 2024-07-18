"""
Db Structure:
**Users Table**
- `user_id` (INT, UNIQUE, AUTO_INCREMENT, PRIMARY KEY)
- `username` (VARCHAR(100), BASE64 ENCODED)
- `first_login_datetime` (DATETIME)
- `last_login_datetime` (DATETIME)
- `first_login_ip` (VARCHAR(45))
- `last_login_ip` (VARCHAR(45))
- `last_song_submission_datetime` (DATETIME)
- `voted_songs_ids` (TEXT, COMMA-SEPARATED LIST OF SONG IDs)
- `submitted_songs_ids` (TEXT, COMMA-SEPARATED LIST OF SONG IDs)

**Songs Table**
- `song_id` (VARCHAR(100), PRIMARY KEY)
- `is_being_hidden` (BOOLEAN)
- `user_id` (INT, FOREIGN KEY REFERENCES Users(user_id))
- `song_name` (VARCHAR(200), BASE64 ENCODED)
- `is_explicit` (BOOLEAN)
- `vote_count` (INT)

**Additional Tables and Relationships**
- **Song_Votes Table** (many-to-many relationship between Users and Songs)
	+ `user_id` (INT, FOREIGN KEY REFERENCES Users(user_id))
	+ `song_id` (VARCHAR(100), FOREIGN KEY REFERENCES Songs(song_id))
	+ `vote_datetime` (DATETIME)
- **Song_Submissions Table** (many-to-many relationship between Users and Songs)
	+ `user_id` (INT, FOREIGN KEY REFERENCES Users(user_id))
	+ `song_id` (VARCHAR(100), FOREIGN KEY REFERENCES Songs(song_id))
	+ `submission_datetime` (DATETIME)

More notes:
**Indexing and Potential Future Expansion**
- Index the `user_id` and `submission_datetime` columns in the Song_Submissions
  table for efficient querying.
- Index the `username` column in the Users table for fast user lookup.
- Add an index on the `voted_songs_ids` and `submitted_songs_ids`columns
  in the Users table to optimize searches for user's voted and submitted songs.
- If the system needs to handle a large number of users or songs,
  partition the tables by date or user_id to improve query performance.
- If system needs to support more advanced features,
  such as song categories, playlists, or social interactions, you can add
  additional tables and relationships as needed.
"""

from flask import Flask
from flask_mysqldb import MySQL

from typing import Any, Optional
from datetime import datetime
import sqlite3
import base64

app = Flask(__name__)
mysql = MySQL(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_database_name'

class DatabaseWrapper:
    def __init__(self, app: Flask, mysql: MySQL, sqlite_file: str = 'database.db'):
        self.app = app
        self.mysql = mysql
        self.sqlite_file = sqlite_file

    def construct_mysql_database(app:Any, mysql:Any) -> int:
        """Creates mysql database

        Args:
            app   -- Flask(__name__)
            mysql -- MySQL(app)

        Return:
            int: 0 if success
        """

        with app.app_context():
            cur = mysql.connection.cursor()

            table_creation_queries = [
                """
                CREATE TABLE IF NOT EXISTS `Users` (
                    `user_id` int AUTO_INCREMENT NOT NULL UNIQUE,
                    `username` varchar(100),
                    `first_login_datetime` datetime,
                    `last_login_datetime` datetime,
                    `first_login_ip` varchar(45),
                    `last_login_ip` varchar(45),
                    `last_song_submission_datetime` datetime,
                    `voted_songs_ids` text,
                    `submitted_songs_ids` text,
                    PRIMARY KEY (`user_id`)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS `Songs` (
                    `song_id` varchar(100) NOT NULL,
                    `is_being_hidden` boolean,
                    `user_id` int,
                    `song_name` varchar(200),
                    `is_explicit` boolean,
                    `vote_count` int,
                    PRIMARY KEY (`song_id`)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS `Song_Votes` (
                    `user_id` int,
                    `song_id` varchar(100),
                    `vote_datetime` datetime
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS `Song_Submissions` (
                    `user_id` int,
                    `song_id` varchar(100),
                    `submission_datetime` datetime
                )
                """
            ]

            foreign_key_constraints = [
                "ALTER TABLE `Songs` ADD CONSTRAINT `Songs_fk2` FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`)",
                "ALTER TABLE `Song_Votes` ADD CONSTRAINT `Song_Votes_fk0` FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`)",
                "ALTER TABLE `Song_Votes` ADD CONSTRAINT `Song_Votes_fk1` FOREIGN KEY (`song_id`) REFERENCES `Songs`(`song_id`)",
                "ALTER TABLE `Song_Submissions` ADD CONSTRAINT `Song_Submissions_fk0` FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`)",
                "ALTER TABLE `Song_Submissions` ADD CONSTRAINT `Song_Submissions_fk1` FOREIGN KEY (`song_id`) REFERENCES `Songs`(`song_id`)"
            ]

            for query in table_creation_queries:
                cur.execute(query)

            for constraint in foreign_key_constraints:
                cur.execute(constraint)

            mysql.connection.commit()
            cur.close()

            print("MySQL database structure created successfully.")
            return 0


    def construct_sqlite_database(db_file:str = "database.db") -> int:
        """Creates sqlite database

        Args:
            db_file -- Database file (default: "database.db")

        Return:
            int: 0 if success else -1
        """


        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()

            tables = {
                "Users": """
                    CREATE TABLE IF NOT EXISTS Users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        first_login_datetime TEXT,
                        last_login_datetime TEXT,
                        first_login_ip TEXT,
                        last_login_ip TEXT,
                        last_song_submission_datetime TEXT,
                        voted_songs_ids TEXT,
                        submitted_songs_ids TEXT
                    )
                """,
                "Songs": """
                    CREATE TABLE IF NOT EXISTS Songs (
                        song_id TEXT PRIMARY KEY,
                        is_being_hidden INTEGER,
                        user_id INTEGER,
                        song_name TEXT,
                        is_explicit INTEGER,
                        vote_count INTEGER,
                        FOREIGN KEY (user_id) REFERENCES Users(user_id)
                """,
                "Song_Votes": """
                    CREATE TABLE IF NOT EXISTS Song_Votes (
                        user_id INTEGER,
                        song_id TEXT,
                        vote_datetime TEXT,
                        FOREIGN KEY (user_id) REFERENCES Users(user_id),
                        FOREIGN KEY (song_id) REFERENCES Songs(song_id)
                    )
                """,
                "Song_Submissions": """
                    CREATE TABLE IF NOT EXISTS Song_Submissions (
                        user_id INTEGER,
                        song_id TEXT,
                        submission_datetime TEXT,
                        FOREIGN KEY (user_id) REFERENCES Users(user_id),
                        FOREIGN KEY (song_id) REFERENCES Songs(song_id)
                    )
                """
            }

            for table_name, create_statement in tables.items():
                cur.execute(create_statement)

            print(f"SQLite database structure created successfully in {db_file}.")
            return 0

    def register_new_user_mysql(username: str, ip: str, app: Any, mysql: Any) -> int:
        """Register a new user in the MySQL database

        Args:
            username (str): The username to register
            ip (str): The IP address of the user
            app: Flask application instance
            mysql: MySQL database instance

        Returns:
            int: The user_id of the newly registered user, or -1 if registration failed
        """
        with app.app_context():
            cur = mysql.connection.cursor()

            # Encode the username to base64 as per the database structure
            encoded_username = base64.b64encode(username.encode()).decode()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = """
            INSERT INTO Users
            (username, first_login_datetime, last_login_datetime, first_login_ip, last_login_ip,
            last_song_submission_datetime, voted_songs_ids, submitted_songs_ids)
            VALUES (%s, %s, %s, %s, %s, NULL, NULL, NULL)
            """
            try:
                cur.execute(query, (encoded_username, current_time, current_time, ip, ip))
                mysql.connection.commit()
                user_id = cur.lastrowid
                cur.close()
                return user_id
            except Exception as e:
                print(f"Error registering new user: {e}")
                mysql.connection.rollback()
                cur.close()
                return -1

    def register_new_user_sqlite(username: str, ip: str, db_file: str = 'database.db') -> int:
        """Register a new user in the SQLite database

        Args:
            username (str): The username to register
            ip (str): The IP address of the user
            db_file (str, optional): The database file path. Defaults to 'database.db'.

        Returns:
            int: The user_id of the newly registered user, or -1 if registration failed
        """
        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()

            # Encode the username to base64 as per the database structure
            encoded_username = base64.b64encode(username.encode()).decode()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = """
            INSERT INTO Users
            (username, first_login_datetime, last_login_datetime, first_login_ip, last_login_ip,
            last_song_submission_datetime, voted_songs_ids, submitted_songs_ids)
            VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)
            """

            try:
                cur.execute(query, (encoded_username, current_time, current_time, ip, ip))
                conn.commit()
                return cur.lastrowid
            except Exception as e:
                print(f"Error registering new user: {e}")
                conn.rollback()
                return -1

    # ----------



        def register_new_user(self, username: str, ip: str, db_type: str = 'mysql') -> int:
            """Register a new user in the database"""
            encoded_username = base64.b64encode(username.encode()).decode()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = """
            INSERT INTO Users
            (username, first_login_datetime, last_login_datetime, first_login_ip, last_login_ip,
            last_song_submission_datetime, voted_songs_ids, submitted_songs_ids)
            VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)
            """

            if db_type == 'mysql':
                with self.app.app_context():
                    cur = self.mysql.connection.cursor()
                    try:
                        cur.execute(query, (encoded_username, current_time, current_time, ip, ip))
                        self.mysql.connection.commit()
                        user_id = cur.lastrowid
                        cur.close()
                        return user_id
                    except Exception as e:
                        print(f"Error registering new user: {e}")
                        self.mysql.connection.rollback()
                        cur.close()
                        return -1
            else:
                with sqlite3.connect(self.sqlite_file) as conn:
                    cur = conn.cursor()
                    try:
                        cur.execute(query, (encoded_username, current_time, current_time, ip, ip))
                        conn.commit()
                        return cur.lastrowid
                    except Exception as e:
                        print(f"Error registering new user: {e}")
                        conn.rollback()
                        return -1

        def get_user_details(self, user_id: int, db_type: str = 'mysql') -> Optional[dict]:
            """Get user details from the database"""
            query = "SELECT * FROM Users WHERE user_id = ?"

            if db_type == 'mysql':
                with self.app.app_context():
                    cur = self.mysql.connection.cursor()
                    cur.execute(query, (user_id,))
                    user = cur.fetchone()
                    cur.close()
            else:
                with sqlite3.connect(self.sqlite_file) as conn:
                    cur = conn.cursor()
                    cur.execute(query, (user_id,))
                    user = cur.fetchone()

            if user:
                return {
                    'user_id': user[0],
                    'username': base64.b64decode(user[1].encode()).decode(),
                    'first_login_datetime': user[2],
                    'last_login_datetime': user[3],
                    'first_login_ip': user[4],
                    'last_login_ip': user[5],
                    'last_song_submission_datetime': user[6],
                    'voted_songs_ids': user[7],
                    'submitted_songs_ids': user[8]
                }
            return None

        def update_user_login(self, user_id: int, ip: str, db_type: str = 'mysql') -> bool:
            """Update user's last login information"""
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "UPDATE Users SET last_login_datetime = ?, last_login_ip = ? WHERE user_id = ?"

            if db_type == 'mysql':
                with self.app.app_context():
                    cur = self.mysql.connection.cursor()
                    try:
                        cur.execute(query, (current_time, ip, user_id))
                        self.mysql.connection.commit()
                        cur.close()
                        return True
                    except Exception as e:
                        print(f"Error updating user login: {e}")
                        self.mysql.connection.rollback()
                        cur.close()
                        return False
            else:
                with sqlite3.connect(self.sqlite_file) as conn:
                    cur = conn.cursor()
                    try:
                        cur.execute(query, (current_time, ip, user_id))
                        conn.commit()
                        return True
                    except Exception as e:
                        print(f"Error updating user login: {e}")
                        conn.rollback()
                        return False

        # Add more methods for song-related operations, voting, etc.

# Example usage:
if __name__ == '__main__':
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'your_username'
    app.config['MYSQL_PASSWORD'] = 'your_password'
    app.config['MYSQL_DB'] = 'your_database_name'
    mysql = MySQL(app)

    db = DatabaseWrapper(app, mysql)
    
    # Create database structure
    db.create_mysql_structure()
    db.create_sqlite_structure()
    
    # Register a new user
    new_user_id = db.register_new_user("new_user", "192.168.1.1")
    print(f"New user registered with id: {new_user_id}")
    
    # Check if username exists
    exists = db.username_exists("new_user")
    print(f"Username 'new_user' exists: {exists}")
    
    # Get user details
    user_details = db.get_user_details(new_user_id)
    print(f"User details: {user_details}")
    
    # Update user login
    updated = db.update_user_login(new_user_id, "192.168.1.2")
    print(f"User login updated: {updated}")