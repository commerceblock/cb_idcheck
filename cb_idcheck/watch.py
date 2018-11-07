from cb_idcheck.database import database
from cb_idcheck.record import record
from cb_idcheck.connectivity import getelementsd 
import os
import pymongo
import datetime
import argparse
import itertools
import time

class watch:
    def __init__(self, dbuser=os.environ.get('MONGODB_USER',None), dbpassword=os.environ.get('MONGODB_PASS',None),
                 port=os.environ.get('MONGODB_PORT', None), host='mongodbhost', 
                 authsource=os.environ.get('MONGODB_USER', None),
                 authmechanism='SCRAM-SHA-256'):
        self.rec = record()        
        self.conf = {} #Ocean daemon config
        self.dbuser=dbuser #Database login details
        self.dbpassword=dbpassword
        self.authsource=authsource
        self.authmechanism=authmechanism
        self.port=port
        self.host=host
        self.count=0

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
        parser.add_argument('--authsource', required=False, default=self.authsource,type=str, help="db authsource")
        parser.add_argument('--authmechanism', required=False, default=self.authmechanism,type=str, help="db authmechanism")
        parser.add_argument('--host', required=False, default=self.host,type=str, help="db host")
        parser.add_argument('--port', required=False, default=self.port,type=str, help="db port")
        args = parser.parse_args(argv)
        self.set_rpcuser(args.rpcuser)
        self.set_rpcpassword(args.rpcpassword)
        self.set_rpcport(args.rpcport)
        self.set_rpcconnect(args.rpcconnect)
        self.dbuser=args.dbuser
        self.dbpassword=args.dbpassword
        self.authsource=args.authsource
        self.authmechanism=args.authmechanism
        self.host=args.host
        self.port=args.port

    def add_keys(self, addresses, keys):
        for address,key in zip(addresses,keys):
            self.ocean.addtowhitelist(str(address), str(key))
            self.count=self.count+1

    def download_keys(self):
        print('downloading all keys from whitelist database to node memory....')
        for document in self.db.whitelist.find():
            self.add_keys(document['addresses'], document['keys'])
        print('download completed.')

    def update_change(self, change):
        print(change)

    def add_change(self, change):
        doc=change['fullDocument']
        self.rec._id=doc['_id']
        self.rec.keys=doc['keys']
        self.rec.addresses=doc['addresses']
        print('adding keys to whitelist for customer id: '+ str(self.rec._id))
        self.add_keys(self.rec.addresses, self.rec.keys)
        print('adding keys completed.')

    def run(self):
        #Start database
        self.db = database(username=self.dbuser, password=self.dbpassword, authsource=self.authsource, authmechanism=self.authmechanism, port=self.port,
                           host=self.host)
        self.db.connect()

        #Connect to node
        self.ocean = getelementsd(self.conf)
        print("connected to node - block count: " + str(self.ocean.getblockcount()))

        self.count=0
        start=time.perf_counter()
        self.download_keys()
        end=time.perf_counter()
        print('downloaded ' + str(self.count) + ' key/address pairs in ' + str(end-start) + ' seconds.')
        
        print('watching database for changes...')
        with self.db.whitelist.watch() as stream:
            for change in stream:
                print('change to db detected:')
                if(change['operationType']=='update'):
                    self.update_change(change)
                if(change['operationType']=='insert'):
                    self.add_change(change)
                print('watching database for changes...')

if __name__ == "__main__":
    from cb_idcheck import watch
    wh=watch.watch()
    wh.parse_args()
    wh.run()




