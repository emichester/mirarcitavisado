import os

os.mkdir("config")
os.mkdir("config/session")

with open("config/session/session.ini","w") as f:
    f.write("""[SESSION]
session_id = 123456789
executor_url = http://127.0.0.1:53189
""")

with open("config/session/shared_file.memory","w") as f:
    f.write("Escritura inicial")

with open("config/data.py","w") as f:
    f.write("""USER_DATA_PATH = "" # ver web https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data
SESSION_PATH = ""

TOKEN = ""
MI_CHAT_ID = 00000
GROUPO_CHAT_ID = -0000

LazyBot_TOKEN = ""
websiteBot_TOKEN = ""
""")