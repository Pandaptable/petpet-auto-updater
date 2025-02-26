import os
from io import BytesIO

from dotenv import load_dotenv
from hata import Client, Permission, User, wait_for_interruption
from hata.discord.http.urls import user_avatar_url
from hata.ext.slash import setup_ext_slash
from petpetgif import petpet

from utils.sql import add_emoji, emoji_exists, fetch_existing_emoji, fetch_user_emojis, init_petpet_db, remove_emoji

load_dotenv()

client = Client(os.getenv("DISCORD_TOKEN"))

setup_ext_slash(client)


@client.events
async def ready(client):
	print("Initializing petpet db...")
	init_petpet_db()
	print("Petpet db initialized!")
	print("Ready!")


@client.events
async def user_update(client, user, old_attributes):
	if "avatar" in old_attributes:
		emoji_list = fetch_user_emojis(user.id)
		if emoji_list:
			for guild_id, emoji_id, emoji_name in emoji_list:
				await client.emoji_delete((guild_id, emoji_id), reason="Avatar changed")
				async with client.http.get(user_avatar_url(user)) as response:
					emoji_data = await response.read()

				emoji_data = BytesIO(emoji_data)
				petpet_output = BytesIO()
				petpet.make(emoji_data, petpet_output)
				petpet_output.seek(0)
				emoji_output = petpet_output.read()

				emoji = await client.emoji_create(guild_id, emoji_output, name=emoji_name)
				add_emoji(user.id, guild_id, emoji_name, emoji.id)


@client.events
async def emoji_delete(client, emoji):
	if emoji_exists(emoji.id):
		remove_emoji(emoji.id)


@client.interactions(integration_context_types=["guild"], is_global=True, required_permissions=Permission().update_by_keys(create_guild_expressions=True))
async def add_petpet(
	client,
	event,
	user: (User, "The user to add petpet emoji from."),  # type: ignore
	emoji_name: ("str", "The petpet emoji's name."),  # type: ignore
):
	"""Adds an auto updating petpet emoji from user.

	Parameters
	----------
	user : '`ClientUserBase`'
	emoji_name : `str`
	"""

	existing_emoji_id = fetch_existing_emoji(user.id, event.guild_id)
	if existing_emoji_id:
		await client.emoji_delete((event.guild_id, existing_emoji_id), reason="User reran command")

	async with client.http.get(user_avatar_url(user)) as response:
		emoji_data = await response.read()

	emoji_data = BytesIO(emoji_data)
	petpet_output = BytesIO()
	petpet.make(emoji_data, petpet_output)
	petpet_output.seek(0)

	emoji_output = petpet_output.read()

	emoji = await client.emoji_create(event.guild_id, emoji_output, name=emoji_name)
	add_emoji(user.id, event.guild_id, emoji_name, emoji.id)

	return f"Created petpet emoji: <a:{emoji_name}:{emoji.id}>"


client.start()

wait_for_interruption()
