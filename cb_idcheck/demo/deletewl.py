#Deletes the entire whitelist collection from the mongodb database

from cb_idcheck.database import database 

print("Connecting to db...")
db = database()
db.connect()

print("Deleting all entries in the whitelist...")
db.whitelist.delete_many({})

