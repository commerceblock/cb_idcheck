#Fetches the addresses and keys from the whitelist database and prints them in columns <address> <key>
from cb_idcheck.database import database

db = database()
db.connect()
for document in db.whitelist.find():
    print(document['_id'])
    print(document['created_utc'])
    print(document['updated_utc'])
    keys=document['keys']
    addresses=document['addresses']
    for key, address in zip(keys, addresses):
        print (address, key)
