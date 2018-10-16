import datetime
import pprint
import pymongo
import urllib.parse
import sys
from cb_idcheck.record import record
import os

class database:
    def __init__(self,username=None, password=None, 
                 port=27018, host='mongodbhost', authSource='testnet_iddb',authMechanism='SCRAM-SHA-256'):
        self.username = urllib.parse.quote_plus(raw_input("MongoDB username: "))
        self.password = urllib.parse.quote_plus(raw_input("password: "))
        self.port=port
        self.host=host
        self.authSource=authSource
        self.authMechanism=authMechanism

    def connect(self):
        self.client = pymongo.MongoClient(self.host,
                     port=self.port,
                      username=self.username,
                      password=self.password,
                      authSource=self.authSource,
                      authMechanism=self.authMechanism)
        self.db = self.client[self.authSource]
        self.whitelist=self.db.whitelist

    def addToWhitelist(self, customer_record : record):
        return self.whitelist.insert_one(customer_record.get()).inserted_id

    def getFromID(self,_id):
        return self.whitelist.find_one({"_id" : _id})

    def test(self, keyFile=None):
        self.connect()
        customer1 = record('customer-00001')
        customer2 = record('customer-00002')

        if(keyFile):
            customer1.importKeys(keyFile)
            
        else:
            customer1.keys=['4rt34rt34t4323', '43g349843rt34']
            customer1.addresses=['32r23f908h23f098h23','32f08hj23f09823f']

        customer2.keys=['f348hg0832gf','f238fh2938hf98']
        customer2.addresses=['0294jf0q23hfg0q93efgh','qe8fh98hq349fh89']


        print("Record for customer 1.")
        print(customer1.get())

        print("Records in db:")
        print(self.whitelist)

        print("Insert record into db - cust_id_1:")
        cust_id_1=self.addToWhitelist(customer1)
        print(cust_id_1)

        print("Fetch the customer record using the _id")
        pprint.pprint(self.getFromID(customer1._id))

        print("Fetch a non-existent customer")
        pprint.pprint(self.getFromID(customer2._id))

        print("Add customer2 to the whitelist")
        cust_id_2 = self.addToWhitelist(customer2)
        print(cust_id_2)

        print("Fetch customer2")
        pprint.pprint(self.getFromID(customer2._id))

        print("Fetch the customer record that contains the customer1.addresses")
        pprint.pprint(self.whitelist.find_one({'addresses' : customer1.addresses}))

        print("Fetch the customer record that contains the first key belonging to customer 2")
        pprint.pprint(self.whitelist.find_one({'keys': customer2.keys[0]}))

        print("Remove customer1 from the db:")
        self.whitelist.remove({"_id" : customer1._id})

        print("Fetch customer1")
        pprint.pprint(self.getFromID(customer1._id))

        print("Remove customer2 from the db:")
        self.whitelist.remove({"_id" : customer2._id})

        print("Fetch customer2")
        pprint.pprint(self.getFromID(customer2._id))

