from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
GROUP_IDS = env.list("GROUP_IDS")
IP = env.str("ip")
