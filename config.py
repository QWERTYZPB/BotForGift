from environs import Env
import os

os.environ.clear()

env = Env()
env.read_env()
# print(env.path())
# admins=env('ADMIN_IDS')
# print('admins:', admins)
ADMIN_IDS: list[int] = list(map(int, env('ADMIN_IDS').split(',')))

BOT_TOKEN = env('BOT_TOKEN')


SERVER_IP=env('SERVER_IP')
