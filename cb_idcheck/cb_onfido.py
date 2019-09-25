# Copyright (c) 2018 The CommerceBlock Developers                                                                                                              
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

#Class inhertied from onfido class for connection to onfido and id check submission/retrieval
import onfido
import os
from onfido.rest import ApiException
from .record import record 
from .database import database
from pprint import pprint
from cb_idcheck import record

class cb_onfido:
      #Set the authentication foken for connection to onfido
      def set_token(self, token):
            self.token=token
            if(self.token != None):
                  self.configuration.api_key['Authorization'] = 'token=' + self.token


      def __init__(self, token=None):
            self.record = record.record()
            self.onfido = onfido
            self.configuration = self.onfido.Configuration()
            self.configuration.api_key_prefix['Authorization'] = 'Token'
            self.api_instance = self.onfido.DefaultApi()
            self.set_token(token)

      def process_webhook_request(self, request):
            applicant_check = self.find_applicant_check(request.json["payload"]["object"]["href"])
            self.record.import_from_applicant_check(applicant_check)
            if(applicant_check[1].result=="clear"):
                  self.record.get()
                  self.record.to_file("whitelisted")
                  print('ID Check result: clear. Added addresses to whitelist.')
                  return 'Added addresses to whitelist.', 200
                #The check returned 'consider' status so human intervention is required.
            elif(applicant_check[1].result=="consider"):
                  self.cust_record.to_file("consider")
                  print('ID Check result: consider. Addding check to considerlist.')
                  return 'Added addresses to considerlist.', 200
            else:
                  return None, None

      #Retrieve report from href.
      def find_report(self,href):
            check_search="/checks/"
            check_start=href.find(check_search)+len(check_search)
            check_end=href.find('/',check_start)
            check_id=href[check_start:check_end]

            report_search="/reports/"
            report_start=href.find(report_search)+len(report_search)
            report_id=href[report_start:]
            
            api_response_report=None

            try:
                  api_response_report = self.api_instance.find_report(check_id, report_id)
            except ApiException as e:
                  pprint(e.body)
                  return None

            return api_response_report

      def find_applicant(self, applicant_id):
            try:
                  return self.api_instance.find_applicant(applicant_id)
            except ApiException as e:
                  pprint(e.body)

      #Retrieves the applicant and check from the href.
      def find_applicant_check(self,href=None, applicant_id=None, check_id=None):
            if((applicant_id == None) or (check_id == None)):
                  if(href != None):
                        applicant_search="/applicants/"
                        applicant_start=href.find(applicant_search)+len(applicant_search)
                        applicant_end=href.find('/',applicant_start)
                        applicant_id=href[applicant_start:applicant_end]

                        check_search="/checks/"
                        check_start=href.find(check_search)+len(check_search)
                        check_id=href[check_start:]
                  else:
                        return None
            
            try:
                  api_response_applicant = self.api_instance.find_applicant(applicant_id)
            except ApiException as e:
                  pprint(e.body)
                  return None

            try:
                  api_response_check = self.api_instance.find_check(applicant_id, check_id)
            except ApiException as e:
                  pprint(e.body)
                  return None

            return [api_response_applicant, api_response_check]


#Retrieves check and report from a href and applicant id.
      def find_check_report(self,href, applicant_id=None):
            check_search="/checks/"
            check_start=href.find(check_search)+len(check_search)
            check_end=href.find('/',check_start)
            check_id=href[check_start:check_end]

            api_response_check=None
            api_response_report=None

            try:
                  api_response_check = self.api_instance.find_check(applicant_id, check_id)
            except ApiException as e:
                  pprint(e.body)
                  return None

            try:
                  api_response_report = self.find_report(href)
            except ApiException as e:
                  pprint(e.body)
                  return None

            return [api_response_check, api_response_report]

      def test(self):
            db = database() 
#Get the data from onfido - the hrefs will be given in the webhook
            applicant_check=self.find_applicant_check('https://api.onfido.com/v2/applicants/2bc75038-4776-464c-807d-7d7ad21a08ce/checks/cd210ae4-f487-43da-9f7a-21de0ac43550')
            rec = record.record()
#Fill a record object
            rec.import_from_applicant_check(applicant_check)
#Upload to MongoDB database
            db.connect()
            print("Whitelist before: ")
            print(db.whitelist)
            print("Adding customer record: ")
            print(rec.get())
            db.addToWhitelist(rec)
            print("Read customer from database using id: "  + rec._id)
            pprint(db.getFromID(rec._id))
            print("Delete customer from database using id: "  + rec._id)
            db.whitelist.remove({"_id" : rec._id})
            print("Read customer from database using id: "  + rec._id)
            pprint(db.getFromID(rec._id))

      def create_webhook(self, url=None):
            pprint("Creating webhook data")
            webhook=onfido.Webhook(url=url)
            self.webhook=None
            try:
                  # Create a webhook
                  self.webhook = self.api_instance.create_webhook(webhook)
                  pprint(self.webhook)
            except ApiException as e:
                  pprint(e.body)
            return self.webhook

      def list_checks(self, customer_id):
            #Find all checks for customer and put them in an array
            checks_list = []
            templist= []
            n_page=1
            while(True):
                  try:
                        templist=self.api_instance.list_checks(customer_id, page=n_page)
                  except ApiException as e:
                        pprint(e.body)
                  length = len(templist.checks)
                  if(len(templist.checks)>0):
                        checks_list.extend(templist.checks)
                  else:
                        break
                  n_page = n_page+1
            return checks_list


      def list_reports(self, check_id):
            #Find all reports for a check and put them in an array
            reports_list = []
            templist= []
            n_page=1
            try:
                  reports_list=self.api_instance.list_reports(check_id)
            except ApiException as e:
                  pprint(e.body)
            return reports_list.reports

      def destroy_applicant(self, applicant_id):
            try:
                  self.api_instance.destroy_applicant(applicant_id)
            except ApiException as e:
                  pprint(e.body)
            
if __name__ == "__main__":
      from cb_idcheck import cb_onfido
      cb_onfido.cb_onfido().test()

