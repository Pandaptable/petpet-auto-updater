from hata import Client

client: Client


@client.events  # noqa: F821
async def ready(client):
	print("Ready!")


@client.events  # noqa: F821
async def unknown_dispatch_event(client, event):
	print(event)
