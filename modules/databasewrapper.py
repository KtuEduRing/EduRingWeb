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
  such as song categories, playlists, or social interactions, add
  additional tables and relationships as needed.
"""

from flask import Flask
from flask_mysqldb import MySQL

from typing import Optional
from datetime import datetime
import sqlite3
import base64

class DatabaseWrapper:
    def __init__(self, app: Flask, db_type: str = 'mysql', mysql: MySQL = None, sqlite_file: str = 'database.db'):
        self.app = app
        self.db_type = db_type
        self.mysql = mysql
        self.sqlite_file = sqlite_file

    def construct_mysql_database(self) -> int:
        """Creates mysql database if not already exist

        Args:
            app   -- Flask(__name__)
            mysql -- MySQL(app)

        Return:
            int: 0 if success, 1 if already exists
        """

        with self.app.app_context():
            cur = self.mysql.connection.cursor()

            # Check if the database structure already exists
            cur.execute("SHOW TABLES")
            existing_tables = cur.fetchall()
            if existing_tables:
                print("MySQL database structure already exists.")
                cur.close()
                return 1

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

            self.mysql.connection.commit()
            cur.close()

            print("MySQL database structure created successfully.")
            return 0


    def construct_sqlite_database(db_file:str = "database.db") -> int:
        """Creates sqlite database if not already exist

        Args:
            db_file -- Database file (default: "database.db")

        Return:
            int: 0 if success, 1 if already exists, -1 if error
        """

        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()

            # Check if the database structure already exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = cur.fetchall()
            if existing_tables:
                print(f"SQLite database structure already exists in {db_file}.")
                return 1

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
                    )
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


    def register_new_user(self, username: str, ip: str) -> int:
        """Register a new user in the database

        Args:
            username (str): _description_
            ip (str): _description_
            db_type (str, optional): _description_. Defaults to 'mysql'.

        Returns:
            int: -1 error
        """

        encoded_username = base64.b64encode(username.encode()).decode()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = """
        INSERT INTO Users
        (username, first_login_datetime, last_login_datetime, first_login_ip, last_login_ip,
        last_song_submission_datetime, voted_songs_ids, submitted_songs_ids)
        VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)
        """

        if self.db_type == 'mysql':
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
        else:  # SQLite
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

    def user_exists(self, username: str) -> bool:
        """
        Check if a user is registered in the database

        Args:
            username (str): The username to check
            db_type (str, optional): The type of database to use. Defaults to 'mysql'.

        Returns:
            bool: True if the user is registered, False otherwise
        """
        encoded_username = base64.b64encode(username.encode()).decode()

        query = "SELECT user_id FROM Users WHERE username = ?"

        try:
            if self.db_type == 'mysql':
                with self.app.app_context():
                    cur = self.mysql.connection.cursor()
                    cur.execute(query, (encoded_username,))
                    result = cur.fetchone()
                    cur.close()
            else:  # SQLite
                with sqlite3.connect(self.sqlite_file) as conn:
                    cur = conn.cursor()
                    cur.execute(query, (encoded_username,))
                    result = cur.fetchone()

            return result is not None

        except Exception as e:
            print(f"Error checking if user is registered: {e}")
            return False


    def get_user_details(self, user_id: int) -> Optional[dict]:
        """Get user details from the database

        Args:
            user_id (int): _description_
            db_type (str, optional): _description_. Defaults to 'mysql'.

        Returns:
            Optional[dict]: _description_
        """

        query = "SELECT * FROM Users WHERE user_id = ?"

        if self.db_type == 'mysql':
            with self.app.app_context():
                cur = self.mysql.connection.cursor()
                cur.execute(query, (user_id,))
                user = cur.fetchone()
                cur.close()
        else:  # SQLite
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

    def update_user_login_info(self, user_id: int, ip: str) -> bool:
        """Update user's last login information

        Args:
            user_id (int): _description_
            ip (str): _description_
            db_type (str, optional): _description_. Defaults to 'mysql'.

        Returns:
            bool: _description_
        """

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "UPDATE Users SET last_login_datetime = ?, last_login_ip = ? WHERE user_id = ?"

        if self.db_type == 'mysql':
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
        else:  # SQLite
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

    def update_username(self, user_id: int, new_username: str) -> bool:
        """Update user's username

        Args:
            user_id (int): _description_
            new_username (str): _description_
            db_type (str, optional): _description_. Defaults to 'mysql'.

        Returns:
            bool: _description_
        """

        query = "UPDATE Users SET username = ? WHERE user_id = ?"

        if self.db_type == 'mysql':
            cur = self.mysql.connection.cursor()
            with self.app.app_context():
                try:
                    cur.execute(query, (new_username, user_id))
                    cur.commit()
                    cur.close()
                    return True
                except Exception as e:
                    print(f"Error updating username: {e}")
                    cur.rollback()
                    return False

        else:  # SQLite
            with sqlite3.connect(self.sqlite_file) as conn:
                cur = conn.cursor()
                try:
                    cur.execute(query, (new_username, user_id))
                    conn.commit()
                    return True
                except Exception as e:
                    print(f"Error updating username: {e}")
                    conn.rollback()
                    return False

    def submit_song(self, user_id: int, song_id: str, song_name: str, is_explicit: bool) -> bool:
        """
        Submit a song to the database

        Args:
            user_id (int): The ID of the user submitting the song
            song_id (str): The ID of the song being submitted
            song_name (str): The name of the song
            is_explicit (bool): Whether the song contains explicit content
            db_type (str, optional): The type of database to use. Defaults to 'mysql'.

        Returns:
            bool: True if the submission was successful, False otherwise
        """
        encoded_song_name = base64.b64encode(song_name.encode()).decode()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # SQL queries
        insert_song_query = """
        INSERT INTO Songs (song_id, is_being_hidden, user_id, song_name, is_explicit, vote_count)
        VALUES (?, FALSE, ?, ?, ?, 0)
        """

        insert_submission_query = """
        INSERT INTO Song_Submissions (user_id, song_id, submission_datetime)
        VALUES (?, ?, ?)
        """

        update_user_query = """
        UPDATE Users
        SET last_song_submission_datetime = ?,
            submitted_songs_ids = CASE
                WHEN submitted_songs_ids IS NULL THEN ?
                ELSE CONCAT(submitted_songs_ids, ',', ?)
            END
        WHERE user_id = ?
        """

        if self.db_type == 'mysql':
            with self.app.app_context():
                cur = self.mysql.connection.cursor()
                try:
                    cur.execute(insert_song_query, (song_id, user_id, encoded_song_name, is_explicit))
                    cur.execute(insert_submission_query, (user_id, song_id, current_time))
                    cur.execute(update_user_query, (current_time, song_id, song_id, user_id))
                    self.mysql.connection.commit()
                    cur.close()
                    return True
                except Exception as e:
                    print(f"Error submitting song: {e}")
                    self.mysql.connection.rollback()
                    cur.close()
                    return False
        else:  # SQLite
            with sqlite3.connect(self.sqlite_file) as conn:
                cur = conn.cursor()
                try:
                    cur.execute(insert_song_query, (song_id, user_id, encoded_song_name, is_explicit))
                    cur.execute(insert_submission_query, (user_id, song_id, current_time))
                    cur.execute(update_user_query, (current_time, song_id, song_id, user_id))
                    conn.commit()
                    return True
                except Exception as e:
                    print(f"Error submitting song: {e}")
                    conn.rollback()
                    return False

    def get_songs_and_info(self) -> Optional[dict]:
        """
        Get all songs and their related information from the database

        Args:
            db_type (str, optional): The type of database to use. Defaults to 'mysql'.

        Returns:
            Optional[dict]: A dictionary containing song details and associated user information,
                            or None if there was an error or no songs were found.
        """

        query = """
        SELECT s.song_id, s.is_being_hidden, s.user_id, s.song_name, s.is_explicit, s.vote_count,
            u.username, u.last_login_datetime, u.last_login_ip
        FROM Songs s
        JOIN Users u ON s.user_id = u.user_id
        """

        try:
            if self.db_type == 'mysql':
                with self.app.app_context():
                    cur = self.mysql.connection.cursor(dictionary=True)
                    cur.execute(query)
                    songs = cur.fetchall()
                    cur.close()
            else:  # SQLite
                with sqlite3.connect(self.sqlite_file) as conn:
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    cur.execute(query)
                    songs = [dict(row) for row in cur.fetchall()]

            if not songs:
                return None

            result = {}
            for song in songs:
                song_id = song['song_id']
                result[song_id] = {
                    'is_being_hidden': bool(song['is_being_hidden']),
                    'user_id': int(song['user_id']),
                    'song_name': base64.b64decode(song['song_name'].encode()).decode(),
                    'is_explicit': bool(song['is_explicit']),
                    'vote_count': int(song['vote_count']),
                    'submitter_username': base64.b64decode(song['username'].encode()).decode(),
                    'submitter_last_login': song['last_login_datetime'],
                    'submitter_last_ip': song['last_login_ip']
                }

            print(f"Songs info: {result}")
            return result

        except Exception as e:
            print(f"Error fetching songs and info: {e}")
            return None

    # def vote_song(self, user_id: int, song_id: str): pass
    def vote_song(self, user_id: int, song_id: str) -> bool:
        """
        Allow a user to vote for a song

        Args:
            user_id (int): The ID of the user voting
            song_id (str): The ID of the song being voted for
            db_type (str, optional): The type of database to use. Defaults to 'mysql'.

        Returns:
            bool: True if the vote was successful, False otherwise
        """

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # SQL queries
        check_vote_query = """
        SELECT * FROM Song_Votes WHERE user_id = ? AND song_id = ?
        """
        insert_vote_query = """
        INSERT INTO Song_Votes (user_id, song_id, vote_datetime)
        VALUES (?, ?, ?)
        """
        update_song_query = """
        UPDATE Songs SET vote_count = vote_count + 1 WHERE song_id = ?
        """
        update_user_query = """
        UPDATE Users
        SET voted_songs_ids = CASE
            WHEN voted_songs_ids IS NULL THEN ?
            ELSE CONCAT(voted_songs_ids, ',', ?)
        END
        WHERE user_id = ?
        """

        try:
            if self.db_type == 'mysql':
                with self.app.app_context():
                    cur = self.mysql.connection.cursor()

                    # Check if user has already voted for this song
                    cur.execute(check_vote_query, (user_id, song_id))
                    if cur.fetchone():
                        cur.close()
                        return False  # User has already voted

                    # Insert vote, update song vote count, and update user's voted songs
                    cur.execute(insert_vote_query, (user_id, song_id, current_time))
                    cur.execute(update_song_query, (song_id,))
                    cur.execute(update_user_query, (song_id, song_id, user_id))

                    self.mysql.connection.commit()
                    cur.close()
                    return True
            else:  # SQLite
                with sqlite3.connect(self.sqlite_file) as conn:
                    cur = conn.cursor()

                    # Check if user has already voted for this song
                    cur.execute(check_vote_query, (user_id, song_id))
                    if cur.fetchone():
                        return False  # User has already voted

                    # Insert vote, update song vote count, and update user's voted songs
                    cur.execute(insert_vote_query, (user_id, song_id, current_time))
                    cur.execute(update_song_query, (song_id,))
                    cur.execute(update_user_query, (song_id, song_id, user_id))

                    conn.commit()
                    return True

        except Exception as e:
            print(f"Error voting for song: {e}")
            if self.db_type == 'mysql':
                self.mysql.connection.rollback()
            else:
                conn.rollback()
            return False

# if __name__ == '__main__':
#     app = Flask(__name__)
#     app.config['MYSQL_HOST'] = 'localhost'
#     app.config['MYSQL_USER'] = 'your_username'
#     app.config['MYSQL_PASSWORD'] = 'your_password'
#     app.config['MYSQL_DB'] = 'your_database_name'
#     mysql = MySQL(app)

#     db = DatabaseWrapper(app, mysql)

#     db.construct_mysql_database()
#     db.construct_sqlite_database()

#     new_user_id = db.register_new_user("new_user", "192.168.1.1")
#     print(f"New user registered with id: {new_user_id}")

#     exists = db.username_exists("new_user")
#     print(f"Username 'new_user' exists: {exists}")

#     user_details = db.get_user_details(new_user_id)
#     print(f"User details: {user_details}")

#     updated = db.update_user_login_info(new_user_id, "192.168.1.2")
#     print(f"User login updated: {updated}")
