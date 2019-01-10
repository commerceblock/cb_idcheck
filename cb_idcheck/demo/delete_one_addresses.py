#Deletes addresses and keys only, leaving the id fields intact.

from cb_idcheck.database import database 

print("Connecting to db...")
db = database()
db.connect()

print("Removing all addresses and keys...")
db.whitelist.update_many({},{'$unset' :{'addresses':"", 'keys':""}})


