#Fetches the addresses and keys from the whitelist database and prints them in columns <address> <key>
from database import *

db = database()
db.connect()
for document in db.whitelist.find():
    document
    keys=document['keys']
    addresses=document['addresses']
    for key, address in zip(keys, addresses):
        print (address, key)
