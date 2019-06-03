# Copyright (c) 2018 The CommerceBlock Developers                                                                                                              
# Distributed under the MIT software license, see the accompanying                                                                                             # file LICENSE or http://www.opensource.org/licenses/mit-license.php.  

#Deletes addresses and keys only, leaving the id fields intact.

from cb_idcheck.database import database 
import argparse

def parse_args(argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--id', required=True, type=str, help="document id string")
        args = parser.parse_args(argv)
        return args

if __name__ == "__main__":
    args=parse_args()
    
    print("Connecting to db...")
    db = database()
    db.connect()

    print("Removing document: ")
    print(args.id)
    db.removeFromID(_id=args.id)
    print("Finished.")

