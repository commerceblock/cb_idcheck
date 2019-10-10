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
      def __init__(self, token=None, whitelisted_dir="whitelisted", consider_dir="consider"):
            self.whitelisted_dir=whitelisted_dir
            self.consider_dir=consider_dir
            self.record = record.record()
            self.onfido = onfido
            self.configuration = self.onfido.Configuration()
            self.configuration.api_key_prefix['Authorization'] = 'Token'
            self.api_instance = self.onfido.DefaultApi()
            if token:
                  self.configuration.api_key['Authorization'] = 'token=' + token

      def process_webhook_request(self, request):
            return self.get_kycfile_from_href(request.json["payload"]["object"]["href"])

      def get_kycfile_from_href(self, href):
            applicant_check = self.find_applicant_check(href)
            return self.get_kycfile_from_applicant_check(applicant_check)

      def get_checkid_from_request(self, req):
            return self.get_checkid_from_href(request.json["payload"]["object"]["href"])

      def get_checkid_from_href(self, href):
            applicant_check = self.find_applicant_check(href)
            return appliccant_check[1].id

      def get_kycfile_from_applicant_check(self, applicant_check):
            if self.record.import_from_applicant_check(applicant_check) == False:
                  self.record.to_file(self.consider_dir)
                  message = 'ID Check result: import_from_applicant_check failed. Added kycfile to consider dir. check-id:' + str(applicant_check[1].id)
                  print(message)
                  return message, None
            if(applicant_check[1].result=="clear"):
                  self.record.get()
                  self.record.to_file(self.whitelisted_dir)
                  message = 'ID Check result: clear. Added kycfile to whitelisted dir. check-id:' + str(applicant_check[1].id)
                  print(message)
                  return message, 200
                #The check returned 'consider' status so human intervention is required.
            elif(applicant_check[1].result=="consider"):
                  self.record.to_file(self.consider_dir)
                  message = 'ID Check result: consider. Added kycfile to consider dir. check-id:' + str(applicant_check[1].id)
                  print(message)
                  return message, None
            else:
                  message = 'Unknown ID check result. check-id:' + str(applicant_check[1].id)
                  print(message)
                  return message, None
            
            
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
            n_page=1
            while(True):
                  templist=None
                  try:
                        templist=self.api_instance.list_checks(customer_id, page=n_page)
                  except ApiException as e:
                        logging.warning(e.body)
                        break
                  if templist == None:
                        break
                  length = len(templist.checks)
                  if(len(templist.checks)>0):
                        checks_list.extend(templist.checks)
                  else:
                        break
                  n_page = n_page+1
            return checks_list


      def list_reports(self, check_id):
            #Find all reports for a check and put them in an array
            n_page=1
            reports_list = None
            try:
                  reports_list=self.api_instance.list_reports(check_id)
            except ApiException as e:
                  logging.warning(e.body)
            if reports_list == None:
                  return []
            return reports_list.reports

      def destroy_applicant(self, applicant_id):
            try:
                  self.api_instance.destroy_applicant(applicant_id)
            except ApiException as e:
                  pprint(e.body)
            
if __name__ == "__main__":
      from cb_idcheck import cb_onfido
      cb_onfido.cb_onfido().test()

