from flask import Flask, request, abort
from flask_debug import Debug
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
        self.webhook_key = urllib.parse.quote_plus(os.environ.get('ONFIDO_WEBHOOK_TOKEN'))
        logging.basicConfig(filename='/usr/local/var/log/cb_idcheck_auth.log', level=logging.WARNING)

    def authenticate(self, token, request):
        """
        Calculate signature and return True if it matches header.

        Args:
        token: string, the webhook_token.
        request: an HttpRequest object from which the body content and
        X-Signature header will be extracted and matched.
        
        Returns True if there is a match.

        """
        try:
            signature = request.META['HTTP_X_SIGNATURE']
            logging.debug("Onfido callback X-Signature: %s", signature)
            logging.debug("Onfido callback request body: %s", request.body)
            return _hmac(token, request.body) == signature
        except KeyError:
            logging.warning("Onfido callback missing X-Signature - this may be an unauthorised request.")
            return False
        except Exception:
            logging.exception("Error attempting to decode Onfido signature.")
            return False

    def start(self):
        #Connect to the whitelist database server
        self.db.connect()
        #Route the webhook
        @self.app.route(self.route, methods=['POST'])
        def webhook():
            #First: authenticate the message.
            if not self.authenticate(self.webhook_key, request):
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
        app = Flask(__name__)
        Debug(app)
        self.app.run(host='localhost', port='57398', debug=True)
        

if __name__ == "__main__":
    from cb_idcheck import webhook
    webhook().run()


