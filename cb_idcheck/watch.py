from cb_idcheck import database
from cb_idcheck import record 
import os
import pymongo
import datetime

class watch:
    def __init__(self):
        self.db = database(username=os.environ['TESTNET_MONGODB_U'], 
                      password=os.environ['TESTNET_MONGODB_PW'])
        self.db.connect()
        self.rec = record()        
        self.command="e1-cli readwhitelist "

    def watch(self):
        print('watch started.')
        with self.db.whitelist.watch() as stream:
            for change in stream:
                print('change detected.')
                self.rec._id=change['_id']
                self.rec.keys = change['keys']
                self.rec.addresses=change['addresses']
                result=rec.get()
                filename="wl_" + self.rec._id + "_" + datetime.date + ".keys" 
                with open("wl_" + self.rec._id + "_" + datetime.date + ".keys", 'w') as f:
                    print(result, filename, file=f)
                full_command=self.command + filename
                returnval=os.system(full_command)
                #Need to confirm that the local whitelist node has been updated successfully...
                print(returnval)

if __name__ == "__main__":
    from cb_idcheck import watch
    watch().watch()

