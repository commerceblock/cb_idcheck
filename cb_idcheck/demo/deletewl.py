# Copyright (c) 2018 The CommerceBlock Developers                                                                                                              
# Distributed under the MIT software license, see the accompanying                                                                                             # file LICENSE or http://www.opensource.org/licenses/mit-license.php.

#Deletes the entire whitelist collection from the mongodb database

from cb_idcheck.database import database 

print("Connecting to db...")
db = database()
db.connect()

print("Deleting all entries in the whitelist...")
db.whitelist.delete_many({})

