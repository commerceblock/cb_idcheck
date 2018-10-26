from cb_idcheck import database
from cb_idcheck import record
from federation.test_framework.authproxy import JSONRPCException
from federation.connectivity import getelementsd 
import os
import pymongo
import datetime
import argparse
import itertools

class watch:
    def __init__(self):
        self.rec = record.record()        
        self.conf = {} #Ocean daemon config
        self.dbuser="" #Database login details
        self.dbpassword=""

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
        parser.add_argument('--dbuser', required=False, default=os.environ['TESTNET_MONGODB_U'],type=str, help="Whitelist database user name")
        parser.add_argument('--dbpassword', required=False, default=os.environ['TESTNET_MONGODB_PW'],type=str, help="Whitelist database password")
        args = parser.parse_args(argv)
        self.set_rpcuser(args.rpcuser)
        self.set_rpcpassword(args.rpcpassword)
        self.set_rpcport(args.rpcport)
        self.set_rpcconnect(args.rpcconnect)
        self.dbuser=args.dbuser
        self.dbpassword=args.dbpassword

    def run(self):
        #Start database
        print(self.dbuser)
        print(self.dbpassword)
        self.db = database.database(username=self.dbuser, password=self.dbpassword)
        self.db.connect()

        #Connect to node
        self.ocean = getelementsd(self.conf)
        print("Block count: " + str(self.ocean.getblockcount()))

        print('watch started.')
        with self.db.whitelist.watch() as stream:
            for change in stream:
                print('change to db detected.')
                self.rec._id=change['_id']
                self.rec.keys = change['keys']
                self.rec.addresses=change['addresses']
                print('adding keys to whitelist for id: '+ str(self.rec._id))
                for address,key in itertools.izip(self.rec.addresses,self.rec.keys):
                    self.ocean.addtowhitelist(key, address)




if __name__ == "__main__":
    from cb_idcheck import watch
    wh=watch.watch()
    wh.parse_args()
    wh.run()




