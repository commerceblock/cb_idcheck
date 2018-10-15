from __future__ import print_function
import time
import datetime
import onfido
from onfido.rest import ApiException
from pprint import pprint

# Configure API key authorization: Token
onfido.configuration.api_key['Authorization'] = 'token=' + 'YOUR_API_KEY'
onfido.configuration.api_key_prefix['Authorization'] = 'Token'
# create an instance of the API class
api_instance = onfido.DefaultApi()

# setting applicant details
applicant = onfido.Applicant()
applicant.first_name = 'John'
applicant.last_name = 'Smith'
applicant.dob = datetime.date(1980, 1, 22)
applicant.country = 'GBR'

address = onfido.Address()
address.building_number = '100'
address.street = 'Main Street'
address.town = 'London'
address.postcode = 'SW4 6EH'
address.country = 'GBR'

applicant.addresses = [address]

# setting check request details
check = onfido.CheckCreationRequest()
check.type = 'express'

report = onfido.Report()
report.name = 'identity'

check.reports = [report]

try:
    # Create Applicant
    api_response = api_instance.create_applicant(data=applicant)
    applicant_id = api_response.id
    api_response = api_instance.create_check(applicant_id, data=check)
    pprint(api_response)
except ApiException as e:
    pprint(e.body)
