import os

from dotenv import load_dotenv
from hata import Client, wait_for_interruption
from hata.ext.plugin_loader import add_default_plugin_variables, register_and_load_plugin
from hata.ext.slash import setup_ext_slash

load_dotenv()

client = Client(os.getenv("DISCORD_TOKEN"))

setup_ext_slash(client)

add_default_plugin_variables(client=client)

register_and_load_plugin("plugins/petpet")


client.start()

wait_for_interruption()
