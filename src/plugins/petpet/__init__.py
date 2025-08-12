from io import BytesIO
from time import perf_counter

from hata import Client, Permission, User
from hata.discord.http.urls import user_avatar_url
from petpetgif import petpet

from utils.sql import add_emoji, emoji_exists, fetch_existing_emoji, fetch_user_emojis, init_petpet_db, remove_emoji

client: Client


@client.events  # noqa: F821
async def ready(client):
	start = perf_counter()
	print("Starting petpet plugin")
	print("Initializing petpet db...")
	init_petpet_db()
	print("Petpet db initialized!")
	delay = (perf_counter() - start) * 1000.0
	print(f"Initialization took {delay:.0f}ms")
	print("Petpet plugin started")


@client.events  # noqa: F821
async def user_update(client, user, old_attributes):
	if "avatar" in old_attributes:
		emoji_list = fetch_user_emojis(user.id)
		if emoji_list:
			for guild_id, emoji_id, emoji_name in emoji_list:
				avatar_url = user_avatar_url(user)

				async with client.http.get(avatar_url) as response:
					content_type = response.headers.get("content-type", "").lower()
					content_types = ["image/jpeg", "image/png", "image/gif"]
					if content_type not in content_types:
						return "User has an invalid avatar."

					emoji_data = await response.read()

				await client.emoji_delete((guild_id, emoji_id), reason="Avatar changed")
				emoji_data = BytesIO(emoji_data)
				petpet_output = BytesIO()
				petpet.make(emoji_data, petpet_output)
				petpet_output.seek(0)
				emoji_output = petpet_output.read()

				emoji = await client.emoji_create(guild_id, emoji_output, name=emoji_name)
				add_emoji(user.id, guild_id, emoji_name, emoji.id)


@client.events  # noqa: F821
async def emoji_delete(client, emoji):
	if emoji_exists(emoji.id):
		remove_emoji(emoji.id)


@client.interactions(integration_context_types=["guild"], is_global=True, required_permissions=Permission().update_by_keys(create_guild_expressions=True))  # noqa: F821
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
	emoji_name : `str`/add
	"""

	avatar_url = user_avatar_url(user)

	async with client.http.get(avatar_url) as response:
		content_type = response.headers.get("content-type", "").lower()
		if content_type != "image/png":
			return "User has an invalid avatar."

		emoji_data = await response.read()

	existing_emoji_id = await fetch_existing_emoji(user.id, event.guild_id)
	if existing_emoji_id is not None:
		await client.emoji_delete((event.guild_id, existing_emoji_id), reason="User regenerated gif")

	emoji_data = BytesIO(emoji_data)
	petpet_output = BytesIO()
	petpet.make(emoji_data, petpet_output)
	petpet_output.seek(0)

	emoji_output = petpet_output.read()

	emoji = await client.emoji_create(event.guild_id, emoji_output, name=emoji_name)
	add_emoji(user.id, event.guild_id, emoji_name, emoji.id)

	return f"Created petpet emoji: <a:{emoji_name}:{emoji.id}>"
