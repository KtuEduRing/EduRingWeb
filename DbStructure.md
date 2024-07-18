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