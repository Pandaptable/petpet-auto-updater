import sqlite3


def init_petpet_db():
	with sqlite3.connect("petpet.db") as connection:
		cursor = connection.cursor()
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS emojis(
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INTEGER,
				guild_id INTEGER,
				emoji_name TEXT,
				emoji_id INTEGER,
				UNIQUE(user_id, guild_id)
			)
			"""
		)
		connection.commit()
		cursor.close()



def add_emoji(user_id, guild_id, emoji_name, emoji_id):
	with sqlite3.connect("petpet.db") as connection:
		cursor = connection.cursor()
		cursor.execute(
			"""
			INSERT INTO emojis(user_id, guild_id, emoji_name, emoji_id)
			VALUES(?, ?, ?, ?)
			ON CONFLICT(user_id, guild_id) DO UPDATE
			SET emoji_name = excluded.emoji_name,
				emoji_id = excluded.emoji_id
			""",
			(user_id, guild_id, emoji_name, emoji_id)
		)
		connection.commit()
		cursor.close()


def fetch_user_emojis(user_id):
	with sqlite3.connect("petpet.db") as connection:
		cursor = connection.cursor()
		cursor.execute(
			"""
			SELECT guild_id, emoji_id, emoji_name
			FROM emojis
			WHERE user_id = ?
			""",
			(user_id,)
		)
		result = cursor.fetchall()
		cursor.close()
		return result


def fetch_existing_emoji(user_id, guild_id):
	with sqlite3.connect("petpet.db") as connection:
		cursor = connection.cursor()
		cursor.execute(
			"""
			SELECT emoji_id
			FROM emojis
			WHERE user_id = ? AND guild_id = ?
			""",
			(user_id, guild_id)
		)
		result = cursor.fetchone
		cursor.close()
		return result is not None


def emoji_exists(emoji_id):
	with sqlite3.connect("petpet.db") as connection:
		cursor = connection.cursor()
		cursor.execute(
			"""
			SELECT 1
			FROM emojis
			WHERE emoji_id = ?
			""",
			(emoji_id,)
		)
		result = cursor.fetchone()
		cursor.close()
		return result is not None

def remove_emoji(emoji_id):
	with sqlite3.connect("petpet.db") as connection:
		cursor = connection.cursor()
		cursor.execute(
			"""
			DELETE FROM emojis
			WHERE emoji_id = ?
			""",
			(emoji_id,)
		)
		connection.commit()
		cursor.close()