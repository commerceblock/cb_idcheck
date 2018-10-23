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

class webhook:
    def __init__(self, route='/'):
        self.app = Flask(__name__)
        self.cust_record=record()
        self.id_api=cb_onfido.cb_onfido()
        self.db=database()
        self.route=route
        self.username = urllib.parse.quote_plus(os.environ.get('CB_ONFIDO_WEBHOOK_KEY'))
        logging.basicConfig(filename='/usr/local/var/log/cb_idcheck_auth.log', level=logging.WARNING)

    def authenticate(self, request):
        key = bytes(self.webhook_key, 'utf-8')
        message = request.json
        digester = hmac.new(key=key, msg=bytes(message,'utf-8'), digestmod=hashlib.sha1)
        signature = digester.hexdigest()
        return(signature == request.headers["X-Signature"])

    def start(self):
        #Connect to the whitelist database server
        self.db.connect()
        #Route the webhook
        @self.app.route(self.route, methods=['POST',])
        def webhook():
            #First: authenticate the message.
            if not self.authenticate(request):
                logging.warning('Python package cb_idcheck.webhook: ' + str(datetime.now()) + ': Message to webhook failed authentication. Request data: ' + request.data.decode("utf-8"))
                abort(401) 
            self.request=request
            if request.method == 'POST':
            #Authenticate the message
                myjson = json.loads(request.json)
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
                return '', 200
            else:
                abort(400)
                
    def run(self):
        self.start()
        self.app.run()
        

if __name__ == "__main__":
    from cb_idcheck import webhook
    webhook().run()
