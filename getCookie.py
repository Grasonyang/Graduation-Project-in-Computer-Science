from twikit import Client
from configparser import ConfigParser
import asyncio

# login to twitter
config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
password = config['X']['password']
email = config['X']['email']
# authenticate
client = Client(language='en')

asyncio.run(client.login(auth_info_1=username,
            auth_info_2=email, password=password))
client.save_cookies('cookies.json')
