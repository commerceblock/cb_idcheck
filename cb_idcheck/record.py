#A customer record class for whitelisting.
#The _id is a unique customer identifier.
#Keys are the untweaked public keys and addresses are the contract tweaked addresses.
import csv
import collections
from pprint import pprint
import datetime

class record:
    def __init__(self, _id='',keys=[], addresses=[]):
        self._id=_id #applicant id
        self.addresses=addresses
        self.keys=keys
        self.setDate()
        

    def get(self):
        return { "_id" : self._id,
                "addresses" : self.addresses,
                "keys" : self.keys,
                "date" : self.date } 
    
    #Reads the keys from a key dump file.
    #Lines beginning '#' are comments. 
    #File format is: <address> <key>
    def importKeys(self,keyDumpFile):
          with open(keyDumpFile,'rt') as csvfile:
                keyReader = csv.reader(csvfile, delimiter=' ')                                                                                                                                 
                myDialect = csv.excel
                myDialect.delimiter=' '
                dictReader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile), fieldnames=['address', 'key'],dialect=myDialect)
                for row in dictReader:
                    self.addresses = self.addresses+[row['address']]
                    self.keys = self.keys+[row['key']]

    def setDate(self):
        self.date=datetime.datetime.utcnow()

    #Import the ID and keys from a applicant_check = [applicant, check]
    def import_from_applicant_check(self, applicant_check):
        self._id=applicant_check[0]["id"]
        self.addresses=applicant_check[1]["tags"][0]
        self.keys=applicant_check[1]["tags"][1]

    def test(self, keyFile=None):
        self._id='a_user_supplied_unique_id'
        if(keyFile):
            self.importKeys(keyFile)
        else:
            self.keys=['key1','key2']
            self.addresses=['add1', 'add2']
        pprint(self.get())
    
    


