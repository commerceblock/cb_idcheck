from cb_idcheck import database
from cb_idcheck import record 
import os
import pymongo

class watch:
    def __init__(self):
        db = database(username=os.environ['TESTNET_MONGODB_U'], 
                      password=os.environ['TESTNET_MONGODB_PW'])
        db.connect()
        

    def watch():
        with db.whitelist.watch() as stream:
            for change in stream:
                rec = record.record()
                rec._id=change['_id']
                rec.keys = change['keys']
                rec.addresses=change['addresses']
                result=rec.get()
                print result
