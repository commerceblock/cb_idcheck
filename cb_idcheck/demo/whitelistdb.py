#To be called from ../ocean-demo/whitelistdb.sh

from cb_idcheck import database 
from cb_idcheck import record
import random

print("Generating random customer id and adding keys to record...")
client_rec = cbid_record(random.randint(1,10000))
main_rec = cbid_record(random.randint(1,10000))
client_rec.importKeys('keys.client')
main_rec.importKeys('keys.main')
print('Adding client and main records to db...')
db.addToWhitelist(client_rec)
db.addToWhitelist(main_rec)



