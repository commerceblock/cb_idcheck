from flask import Flask, request, abort
import json
from cb_idcheck import record
from cb_idcheck import cb_onfido
from cb_idcheck import database
from pprint import pprint
import hmac
import hashlib
import logging
from datetime import datetime
import urllib, os

class webhook:
    def __init__(self, route='/'):
        self.app = Flask(__name__)
        self.cust_record=record()
        self.id_api=cb_onfido.cb_onfido()
        self.db=database()
        self.route=route
        self.webhook_key = urllib.parse.quote_plus(os.environ.get('ONFIDO_WEBHOOK_TOKEN', 'No key'))
        logging.basicConfig(filename='/usr/local/var/log/cb_idcheck_auth.log', level=logging.WARNING)

    def authenticate(self, request):
        key = self.webhook_key.encode()
        message = request.data
        auth_code=hmac.new(key, message, hashlib.sha1).hexdigest()
        return(auth_code == request.headers["X-Signature"])

    def start(self):
        #Connect to the whitelist database server
        self.db.connect()
        #Route the webhook
        @self.app.route(self.route, methods=['POST'])
        def webhook():
            #First: authenticate the message.
            if not self.authenticate(request):
                logging.warning('Python package cb_idcheck.webhook: ' + str(datetime.now()) + ': Message to webhook failed authentication. Request data: ' + request.data.decode("utf-8"))
                abort(401) 
            myjson = request.json
            print(myjson)
            #Check that this notification if of type "check.complete":
            if(myjson["payload"]["action"]=="check.completed"):
                #Retrieve the applicant and check from onfido using the href
                applicant_check = self.id_api.find_applicant_check(myjson["payload"]["object"]["href"])
                #If the applicant passed the check...
                if(applicant_check[1].result=="clear"):
#..read the data into a customer record...
                    self.cust_record.import_from_applicant_check(applicant_check)
                    #...and add it to the whitelist database
                    self.db.addToWhitelist(self.cust_record)
                    return 'Added addresses to whitelist.', 200
                #Check that this notification if of type "check.complete":
            if(myjson["payload"]["action"]=="test_action"):
                print('Test successful.')
                return 'Test successful.', 200
            return 'No action taken.', 200
            abort(400)
                
    def run(self):
        self.start()
        self.app.run(host='localhost', port='57398')
        

if __name__ == "__main__":
    from cb_idcheck import webhook
    webhook().run()
