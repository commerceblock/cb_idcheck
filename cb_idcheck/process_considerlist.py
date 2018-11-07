from cb_idcheck.database import database
from cb_idcheck.cb_onfido import cb_onfido
from cb_idcheck.record import record
from pprint import pprint
from pprint import pformat
import json
import webbrowser
import argparse



class process_considerlist:
    def __init__(self):
        self.db=database()
        self.id_api=cb_onfido()


    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--username', required=False, default=self.db.username,type=str, help="DB username")
        parser.add_argument('--password', required=False, default=self.db.password,type=str, help="DB password")
        parser.add_argument('--port', required=False, default=self.db.port,type=str, help="DB port")
        parser.add_argument('--host', required=False, default=self.db.host,type=str, help="DB host")
        parser.add_argument('--authsource', required=False, default=self.db.authsource,type=str, help="DB authSource")
        parser.add_argument('--authmechanism', required=False, default=self.db.authmechanism,type=str, help="DB authMechanism")
        parser.add_argument('--idcheck_token', required=False, type=str, default=self.id_api.token, help="ID check vendor (e.g. Onfido) API token. Default=$IDCHECK_API_TOKEN")
        args=parser.parse_args(argv)
        self.db.username=args.username
        self.db.password=args.password
        self.db.port=args.port
        self.db.host=args.host
        self.db.authsource=args.authsource
        self.db.authmechanism=args.authmechanism
        self.id_api.token=args.idcheck_token

    def main(self):
        print('Processing considerlist...')
        self.db.connect()

#Loop through all applicant records in consider list.
        for document in self.db.considerlist.find():
            print('========Displaying checks for customer ' + document['_id'])
            pprint(self.id_api.find_applicant(document['_id']))
            n_checks_approved=0
            n_checks_rejected=0
    #Loop through all the checks in the applicant record and request a decision from the user.
            checks_list  = self.id_api.list_checks(document['_id'])
            print('There are ' + str(len(checks_list)) + ' checks in considerlist for this applicant. Results urls are: ')
            nCheck=1
            for check in checks_list :
                print(str(nCheck) + ':   ' + check.results_uri)
                nCheck=nCheck+1
                nCheck=1
            for check in checks_list:
                b_sure=False
        #webbrowser.open(check.download_uri, new=0, autoraise=True)
                print('Displaying check result number ' + str(nCheck) + ' in web browser at '  + str(check.results_uri))
                webbrowser.open(check.results_uri, new=0, autoraise=True)
                while(b_sure==False):
                    review_result=input('Result? [accept/reject/quit]: ')
                    prepend=""
                    if(review_result == "quit"):
                        quit()
                    elif(review_result == "accept"):
                        prepend="Confirm \"accept\" "
                    elif(review_result == 'reject'):
                        prepend="Confirm \"reject\""
                    else:
                        print('Please respond accept/reject/quit.')
                        continue
                    sure=""
                    while((sure != 'yes') and (sure !='no') and (sure != 'quit')):
                        sure=input(prepend + '? [yes/no/quit]: ')
                        if(sure=='quit'):
                            quit()
                        elif(sure=='yes'):
                            b_sure=True
                        elif(sure=='no'):
                            b_sure=False
                        else:
                            print("Please respond yes/no/quit.")
        
                if(review_result=='accept'):
                    customer_record = record()
                    customer_record.import_from_applicant_check(self.id_api.find_applicant_check(applicant_id=document['_id'], check_id=check.id))
                    self.db.addToWhitelist(customer_record)
                    n_checks_approved=n_checks_approved+1
                else:
                    n_checks_rejected=n_checks_rejected+1
                nCheck=nCheck+1
            

        
            print('=============================================================================================')
            print('Finished processing checks for applicant ' + document['_id'])
            print('Summary: ')
            print('')
            print('Checks approved:' + str(n_checks_approved))
            print('Checks rejected:' + str(n_checks_rejected))
            remove_ok=input('Remove applicant from consider list? [yes/no]: ')
            if(remove_ok == 'yes'):
                self.db.remove_from_considerlist(document['_id'])
            print('---------------------------------------------------------------------------------------------')

            
        print('')
        print('...finished processing considerlist.')
        
    
if __name__ == "__main__":
    pc = process_considerlist()
    pc.parse_args()
    pc.main()

