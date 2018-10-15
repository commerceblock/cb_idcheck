from flask import Flask, request, abort
import json
import record
import cb_onfido
import database
from pprint import pprint

class webhook:


    def __init__(self, route='/'):
        self.app = Flask(__name__)
        self.cust_record=record.record()
        self.id_api=cb_onfido.cb_onfido()
        self.db=database.database()
        self.route=route

        @self.app.route(self.route, methods=['POST'])
        def webhook():
            if request.method == 'POST':
                print("Request: ")
                print(request.json)
                #Check that this notification if of type "check.complete":
                if(request.json["payload"]["action"]=="check.complete"):
                    #Retrieve the applicant and check from onfido using the href
                    applicant_check = []#self.id_api.find_applicant_check(request.json["payload"]["object"]["href"])
                    print("Applicant: ")
                    print(applicant_check[0])
                    print("Check: ")
                    print(applicant_check[1])
                #If the applicant passed the check...
                    if(applican_check[1]['result']=="clear"):
                    #..read the data into a customer record...
                    #    cust_record.import_from_applicant_check(applicant_check)
                        pprint(cust_record)
                    #...and add it to the whitelist database
#                        db.add_to_whitelist(cust_record)
                return '', 200
            else:
                abort(400)
                
    def run(self):
        self.app.run()


