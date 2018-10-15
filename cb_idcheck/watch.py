from database import database 
import os
import pymongo

db = database(username=os.environ['TESTNET_MONGODB_U'], 
              password=os.environ['TESTNET_MONGODB_PW'])
db.connect()

with db.whitelist.watch() as stream:
    for change in stream:
        print(change)
