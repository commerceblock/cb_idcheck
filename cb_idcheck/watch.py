from cb_idcheck.database import database
from cb_idcheck.record import record
from federation.connectivity import getelementsd 
import os
import pymongo
import datetime
import argparse
import itertools

class watch:
    def __init__(self, dbuser=default=os.environ['MONGODB_USER'], dbpassword=default=os.environ['MONGODB_PASS']):
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

    def updatewhitelist(self, change):
        a=1

    def addtowhitelist(self, change):
        doc=change['fullDocument']
        self.rec._id=doc['_id']
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
        for address,key in zip(self.rec.addresses,self.rec.keys):
            print('key:' + key)
            print('address:' + address)
            self.ocean.addtowhitelist(address, key)

    def run(self):
        #Start database
        print(self.dbuser)
        print(self.dbpassword)
        self.db = database(username=self.dbuser, password=self.dbpassword)
        self.db.connect()

        #Connect to node
        self.ocean = getelementsd(self.conf)
        print("Block count: " + str(self.ocean.getblockcount()))

        print('watch started.')
        with self.db.whitelist.watch() as stream:
            for change in stream:
                print('change to db detected:')
                if(change['operationType']=='update'):
                    self.updatewhitelist(change)
                if(change['operationType']=='insert'):
                    self.addtowhitelist(change)

if __name__ == "__main__":
    from cb_idcheck import watch
    wh=watch.watch()
    wh.parse_args()
    wh.run()




