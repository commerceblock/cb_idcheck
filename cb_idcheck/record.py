# Copyright (c) 2018 The CommerceBlock Developers                                                                                                              
# Distributed under the MIT software license, see the accompanying                                                                                             # file LICENSE or http://www.opensource.org/licenses/mit-license.php.  

#A customer record class for whitelisting.
#The _id is a unique customer identifier.
#Keys are the untweaked public keys and addresses are the contract tweaked addresses.
import csv
import collections
from pprint import pprint

class record:
    def __init__(self, _applicant_id='', _check_id='', first_name='', last_name='', email='', onboard_pub_key='',user_onboard_pub_key='', addresses=''):
        self._applicant_id=_applicant_id 
        self._check_id=_check_id
        self.first_name=first_name
        self.last_name=last_name
        self.email=email
        self.onboard_pub_key=onboard_pub_key
        self.user_onboard_pub_key=user_onboard_pub_key
        self.nbytes=""
        #Encrypted address data
        self.addresses=addresses


    def get(self):
        return { "_applicant_id" : self._applicant_id,
                 "_check_id" : self._check_id,
                 "first_name" : self.first_name,
                 "last_name" : self.last_name,
                 "email" : self.email,
                 "onboard_pub_key" : self.onboard_pub_key,
                 "user_onboard_pub_key" : self.user_onboard_pub_key,
                 "nbytes" : len(self.addresses),
                 "addresses" : self.addresses,
                } 
    

    #Import the ID and keys from a applicant_check = [applicant, check]
    def import_from_applicant_check(self, applicant_check):
        self._applicant_id=applicant_check[0].id
        self.first_name=applicant_check[0].first_name
        self.last_name=applicant_check[0].last_name
        self.email=applicant_check[0].email
        self._check_id=applicant_check[1].id
        self.addresses=""        
        self.nbytes=None
        self.user_onboard_pub_key=None
        self.onboard_pub_key=None

        for tag in applicant_check[1].tags:
            tagItems=str(tag).split(":")
            if tagItems[0] == "add":
                self.addresses+=tagItems[1]
            if tagItems[0] == "addrdata_encrypted":
                self.addresses+=tagItems[1]
            if tagItems[0] == "nbytes":
                self.nbytes=tagItems[1]
            if tagItems[0] == "user_onboard_pub_key":
                self.user_onboard_pub_key=tagItems[1]
            if tagItems[0] == "onboard_pub_key":
                self.onboard_pub_key=tagItems[1]
                
        if len(self.addresses) == 0:
            return False
        if self.nbytes == None:
            return False
        if self.user_onboard_pub_key == None:
            return False
        if self.onboard_pub_key == None:
            return False

        return True
                
    def to_file(self, outdir):
        filename=str(outdir)+"/kyc_"+str(self._check_id)+".dat"
        f=open(filename, 'w')
        f.write("#applicant-id: " + str(self._applicant_id))
        f.write("\n")
        f.write("#check-id: " + str(self._check_id))
        f.write("\n")
        f.write(' '.join((str(self.onboard_pub_key), str(self.user_onboard_pub_key), str(self.nbytes))))
        f.write("\n")
        f.write(str(self.addresses))
        f.close()

    def test(self):
        pprint("test")
    
    
if __name__ == "__main__":
    from cb_idcheck import record
    record().test()

