#A customer record class for whitelisting.
#The _id is a unique customer identifier.
#Keys are the untweaked public keys and addresses are the contract tweaked addresses.
import csv
import collections
from pprint import pprint

class record:
    def __init__(self, _id='',onboard_pub_key='',user_onboard_pub_key='', addresses=''):
        self._id=_id #applicant id
        self.onboard_pub_key=onboard_pub_key
        self.user_onboard_pub_key=user_onboard_pub_key
        self.nbytes=""
        #Encrypted address data
        self.addresses=addresses


    def get(self):
        return { "_id" : self._id,
                "onboard_pub_key" : self.onboard_pub_key,
                "user_onboard_pub_key" : self.user_onboard_pub_key,
                "nbytes" : len(self.addresses),
                "addresses" : self.addresses,
                } 
    

    #Import the ID and keys from a applicant_check = [applicant, check]
    def import_from_applicant_check(self, applicant_check):
        self._id=applicant_check[0].id
        self.addresses=""        
        for tag in applicant_check[1].tags:
            tagItems=str(tag).split(":")
            if tagItems[0] == "add":
                self.addresses+=tagItems[1]
            if tagItems[0] == "nbytes":
                self.nbytes=tagItems[1]
            if tagItems[0] == "user_onboard_pub_key":
                self.user_onboard_pub_key=tagItems[1]
            if tagItems[0] == "onboard_pub_key":
                self.onboard_pub_key=tagItems[1]

    def to_file(self, outdir):
        filename=str(outdir)+"/kyc_"+str(self._id)+".dat"
        f=open(filename, 'w')
        f.write(' '.join((str(self.onboard_pub_key), str(self.user_onboard_pub_key), str(self.nbytes))))
        f.write("\n")
        f.write(str(self.addresses))
        f.close()

    def test(self):
        pprint("test")
    
    
if __name__ == "__main__":
    from cb_idcheck import record
    record().test()

