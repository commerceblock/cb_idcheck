import datetime
import pprint
import pymongo
import urllib.parse
import sys
from cb_idcheck.record import record
import os
import argparse

class database:
    def quote(self, val):
        if(val):
            return urllib.parse.quote_plus(val)
        else:
            return None

    def __init__(self,username=os.environ.get('MONGODB_USER',None), 
                 password=os.environ.get('MONGODB_PASS',None), 
                 port=os.environ.get('MONGODB_PORT', None), host='mongodbhost', 
                 authSource=os.environ.get('MONGODB_USER', None),
                 authMechanism='SCRAM-SHA-256'):
        
        self.username=self.quote(username)
        self.password=self.quote(password)
        self.port=port
        self.host=host
        self.authSource=self.quote(authSource)
        self.authMechanism=self.quote(authMechanism)

    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--username', required=False, default=self.username,type=str, help="Username")
        parser.add_argument('--password', required=False, default=self.password,type=str, help="Password")
        parser.add_argument('--port', required=False, default=self.port,type=str, help="Port")
        parser.add_argument('--host', required=False, default=self.host,type=str, help="Host")
        parser.add_argument('--authsource', required=False, default=self.username,type=str, help="authSource")
        parser.add_argument('--authmechanism', required=False, default=self.authMechanism,type=str, help="authMechanism")
        args = parser.parse_args(argv)
        self.username=self.quote(args.username)
        self.password=self.quote(args.password)
        self.port=args.port
        self.host=args.host
        self.authSource=self.quote(args.authSource)
        self.authMechanism=self.quote(args.authMechanism)



    def connect(self):
        self.client = pymongo.MongoClient(self.host,
                     port=int(self.port),
                      username=self.username,
                      password=self.password,
                      authSource=self.authSource,
                      authMechanism=self.authMechanism)
        self.db = self.client[self.authSource]
        self.whitelist=self.db.whitelist
        self.considerlist=self.db.considerlist

    def addToWhitelist(self, customer_record : record):
        #Update the record using _id as filter. Add the keys and addresses to the arrays, if not already in the arrays. Change the updated date. Insert the record if no such record exists.
        return self.whitelist.update_one({'_id': customer_record._id}, 
                {
                '$addToSet': {
                    'addresses' : { '$each' : customer_record.addresses},
                    'keys' : { '$each' : customer_record.keys}},
        }, upsert=True).upserted_id

    def addToConsiderlist(self, applicant_check):
        #Set the date of the record to the current time.
        #Update the record using _id as filter. Change the updated date. Insert the record if no such record exists.
        #Each applicant can be associates with several checks with varying passports/keys/etc. 
        #Therefore each check need to be considered individually. The check ids are appended to an array.
        return self.considerlist.update_one({'_id': applicant_check[0].id}, 
                {
                '$addToSet':{ 'checks' : applicant_check[1].id},
                }, upsert=True).upserted_id


    def getFromID(self,_id):
        return self.whitelist.find_one({"_id" : _id})

    def removeFromID(self, _id=None):
        self.whitelist.remove({"_id" : _id})

    def remove_from_considerlist(self, _id):
        self.considerlist.remove({"_id" : _id})

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

        print("Finished test.")

if __name__ == "__main__":
    from cb_idcheck import database
    db=database.database()
    db.parse_args()
    db.test()
