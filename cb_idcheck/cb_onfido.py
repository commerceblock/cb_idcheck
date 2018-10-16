#Class inhertied from onfido class for connection to onfido and id check submission/retrieval
import onfido
from onfido.rest import ApiException
from cb_idcheck import record
from pprint import pprint

class cb_onfido:
      #Set the authentication foken for connection to onfido
      def set_token(self, token):
           self.onfido.configuration.api_key['Authorization'] = 'token=' + token

      def __init__(self, token):
            set_token(token)
            __init__(self)

      def __init__(self):
            self.record = record.record()
            self.onfido = onfido
            self.set_token('YOUR_API_KEY')
            self.onfido.configuration.api_key_prefix['Authorization'] = 'Token'
            print(self.onfido.configuration.api_key)
            print(self.onfido.configuration.api_key_prefix)
            self.api_instance = self.onfido.DefaultApi()

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
                  print(api_response_report)
            except ApiException as e:
                  pprint(e.body)
                  return None

            return api_response_report


      #Retrieves the applicant and check from the href.
      def find_applicant_check(self,href):
            applicant_search="/applicants/"
            applicant_start=href.find(applicant_search)+len(applicant_search)
            applicant_end=href.find('/',applicant_start)
            applicant_id=href[applicant_start:applicant_end]

            check_search="/checks/"
            check_start=href.find(check_search)+len(check_search)
            check_id=href[check_start:]

            
            try:
                  api_response_applicant = self.api_instance.find_applicant(applicant_id)
                  print(api_response_applicant)
            except ApiException as e:
                  pprint(e.body)
                  return None

            try:
                  api_response_check = self.api_instance.find_check(applicant_id, check_id)
                  print(api_response_check)
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
                  print(api_response_check)
            except ApiException as e:
                  pprint(e.body)
                  return None

            try:
                  api_response_report = self.find_report(href)
                  print(api_response_report)
            except ApiException as e:
                  pprint(e.body)
                  return None

            return [api_response_check, api_response_report]



