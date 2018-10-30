from cb_idcheck.database import database
from cb_idcheck.record import record
from federation.connectivity import getelementsd 
import os
import pymongo
import datetime
import argparse
import itertools

class watch:
    def __init__(self, dbuser=os.environ['MONGODB_USER'], dbpassword=os.environ['MONGODB_PASS']):
        self.rec = record()        
        self.conf = {} #Ocean daemon config
        self.dbuser=dbuser #Database login details
        self.dbpassword=dbpassword
        

    def set_rpcuser(self, val):
        self.conf["rpcuser"]=val
    def set_rpcpassword(self, val):
        self.conf["rpcpassword"]=val
    def set_rpcport(self, val):
        self.conf["rpcport"]=val
    def set_rpcconnect(self, val):
        self.conf["rpcconnect"]=val
    

    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--rpcconnect', required=True, type=str, help="Client RPC host")
        parser.add_argument('--rpcport', required=True, type=str, help="Client RPC port")
        parser.add_argument('--rpcuser', required=True, type=str, help="RPC username for client")
        parser.add_argument('--rpcpassword', required=True, type=str, help="RPC password for client")
        parser.add_argument('--dbuser', required=False, default=self.dbuser,type=str, help="Whitelist database user name")
        parser.add_argument('--dbpassword', required=False, default=self.dbpassword, help="Whitelist database password")
        args = parser.parse_args(argv)
        self.set_rpcuser(args.rpcuser)
        self.set_rpcpassword(args.rpcpassword)
        self.set_rpcport(args.rpcport)
        self.set_rpcconnect(args.rpcconnect)
        self.dbuser=args.dbuser
        self.dbpassword=args.dbpassword

    def add_keys(self, addresses, keys):

        for address,key in zip(addresses,keys):
            print(address)
            print(key)
            self.ocean.addtowhitelist(str(address), str(key))

    def download_keys(self):
        print('downloading all keys from whitelist database to node memory....')
        for document in self.db.whitelist.find():
            self.add_keys(document['addresses'], document['keys'])

    def update_change(self, change):
        print(change)

    def add_change(self, chang):
        doc=change['fullDocument']
        self.rec._id=doc['_id']

        self.rec.import_keys(doc['keys'])
        self.rec.import_addresses(doc['addresses'])



        keyChangesList=doc['keys']
        self.rec.keys = []
        for keylist in keyChangesList:
            for key in keylist:
                self.rec.keys.append(key)
        addrChangesList=doc['addresses']
        self.rec.addresses = []
        for addrlist in addrChangesList:
            for addr in addrlist:
                self.rec.addresses.append(addr)




        print('adding keys to whitelist for customer id: '+ str(self.rec._id))
        self.add_keys(self.rec.addresses, self.rec.keys)

    def run(self):
        #Start database
        print(self.dbuser)
        print(self.dbpassword)
        self.db = database(username=self.dbuser, password=self.dbpassword)
        self.db.connect()

        #Connect to node
        self.ocean = getelementsd(self.conf)
        print("connected to node - block count: " + str(self.ocean.getblockcount()))

        self.download_keys()
        
        print('watching database for changes...')
        with self.db.whitelist.watch() as stream:
            for change in stream:
                print('change to db detected:')
                if(change['operationType']=='update'):
                    self.update_change(change)
                if(change['operationType']=='insert'):
                    self.add_change(change)

if __name__ == "__main__":
    from cb_idcheck import watch
    wh=watch.watch()
    wh.parse_args()
    wh.run()




