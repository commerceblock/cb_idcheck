# Copyright (c) 2018 The CommerceBlock Developers                                                                                                              
# Distributed under the MIT software license, see the accompanying                                                                                             # file LICENSE or http://www.opensource.org/licenses/mit-license.php.  

from flask import Flask, request, abort
import json
from cb_idcheck import cb_onfido
from pprint import pprint
import hmac
import hashlib
import logging
from datetime import datetime
import urllib, os
import argparse
import subprocess, sys, time
import smtplib
from email.mime.text import MIMEText
from cb_idcheck.idcheck import idcheck

PYTHON=sys.executable
SCRIPT=__file__

class webhook:
    def __init__(self, token=os.environ.get('IDCHECK_WEBHOOK_TOKEN', None), 
                 url=os.environ.get('IDCHECK_WEBHOOK_URL', None), 
                 port=os.environ.get('IDCHECK_WEBHOOK_PORT', None), 
                 log=os.environ.get('IDCHECK_LOG', '/usr/local/var/log/cb_idcheck.log'), 
                 ngrok=False, 
                 host='localhost',
                 idcheck_token=os.environ.get('IDCHECK_API_TOKEN', None)):
        self.app = Flask(__name__)
        self.idcheck_token=idcheck_token
        self.route='/'
        self.url=url
        self.token=token
        self.log=log
        self.ngrok=ngrok
        self.ngrok_process=None
        self.port=port
        self.host=host
        self.idcheck=idcheck()
        self.id_api=None

    def set_id_api(self, id_api=None):
        if id_api == None:
            self.id_api=cb_onfido.cb_onfido(self.idcheck_token)
        else:
            self.id_api=id_api

    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--token', required=False, type=str, help="Webhook token. Default=$IDCHECK_WEBHOOK_TOKEN", default=self.token)
        parser.add_argument('--url', required=False, type=str, help="Webhook url. Default=$IDCHECK_WEBHOOK_URL", default=self.url)
        parser.add_argument('--port', required=False, type=str, help="Webhook port. Default=$IDCHECK_WEBHOOK_PORT", default=self.port)
        parser.add_argument('--host', required=False, type=str, help="Webhook host. Default='localhost'", default=self.host)
        parser.add_argument('--log', required=False, type=str, help="Log file. Default=$IDCHECK_LOG, fallback=/usr/local/var/log/cb_idcheck.log", default=self.log)
        parser.add_argument('--idcheck_token', required=False, type=str, help="ID check vendor (e.g. Onfido) API token. Default=$IDCHECK_API_TOKEN", default=self.idcheck_token)
        parser.add_argument('--ngrok', required=False, type=bool, help="Bool. Expose local web server to the internet using ngrok?", default=self.ngrok)
        parser.add_argument('--id_api', required=False, type=str, help="ID api: local, onfido. Default=onfido", default="onfido")
   
        args = parser.parse_args(argv)
        self.token = args.token
        self.url=args.url
        self.port=args.port
        self.log=args.log
        self.idcheck_token=args.idcheck_token
        self.ngrok=args.ngrok
        self.host=args.host
        if args.id_api == str("onfido"):
            self.id_api = cb_onfido.cb_onfido(self.idcheck_token)
        elif args.id_api == str("local"):
            selfid_api = cb_local.cb_local()
        else:
            sys.exit("Error: unknown id_api: " + args.id_api)
   
    def authenticate(self, request):
        key = urllib.parse.quote_plus(self.token).encode()
        message = request.data
        auth_code=hmac.new(key, message, hashlib.sha1).hexdigest()
        return(auth_code == request.headers["X-Signature"])

    #Expose local web server to the internet (https only)
    def start_ngrok(self):
        self.ngrok_process=subprocess.Popen(["ngrok", "http", "--bind-tls=true", self.port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
    def get_ngrok_tunnel_info(self):
        time.sleep(10)
        self.tunnel_info_process = subprocess.Popen(["curl", "http://127.0.0.1:4040/api/tunnels", "--connect-timeout", "10"], stdout=subprocess.PIPE)
        self.tunnel_info=json.loads(self.tunnel_info_process.communicate()[0].decode("UTF-8"))
        print(self.tunnel_info)
        return self.tunnel_info
        
    def get_ngrok_ipaddress(self):
        self.get_ngrok_tunnel_info()
        self.url=self.tunnel_info['tunnels'][0]['public_url']
        print("Webhook i.p. address: " + self.url)
        print("route: " + self.route)
        return self.url

#Verify that the check includes the prerequisite reports as stated in the config file
    def verify_check_content(self, report_list=None):
        if(report_list==None):
            report_list=self.id_api.list_reports(request.json["payload"]["object"]["id"])
        for report_req in self.idcheck.cfg.check.reports:
            report_found=False
            for report_comp in report_list:
                if(self.compare_reports_by_type(report_req, report_comp)):
                    report_found=True
                    break
            if (report_found == False):
                return False
        return True
            
#Compare the names and variants of the the two reports.
#Unfortunately, the Onfido report query will return a variant as 'standard' by default even if no variant exists for the report type.
#Therefore, as a work-around empty or 'None' variants are replaced with 'standard' for the purposes of this comparison.
    def compare_reports_by_type(self, report1, report2):
        v1=report1.variant
        if(v1 != None):
            v1.strip()
        else:
            v1='standard'
        v2=report2.variant
        if(v2 != None):
            v2.strip()
        else:
            v2='standard'
        if(report1.name != report2.name):
            return False
        if(v1 != v2):
            return False
        return True

    def route_webhook(self):
        @self.app.route(self.route, methods=['POST'])
        def webhook():
            if self.id_api == None:
                self.set_id_api()
            if not self.authenticate(request):
                logging.warning('cb_idcheck.webhook: ' + str(datetime.now()) + ': A request sent to the webhook failed authentication.')
                abort(401) 
            if(request.json["payload"]["action"]=="check.completed"):
                print('completed check received: ')
                pprint(request.json)
                report_list=self.id_api.list_reports(request.json["payload"]["object"]["id"])
                if(self.verify_check_content(report_list) == False):
                    print('ID Check result: check does not contain all the required report types. The required report types are: ' + str(self.idcheck.cfg) +  '. The included report types are: ')
                    pprint(report_list)
                else:
                    message, retval = self.id_api.process_webhook_request(request)
                    if retval != None:
                        print(message)
                        return message, retval
                    else:
                        print('ID Check result: fail')                        
            elif(request.json["payload"]["action"]=="test_action"):
                print('Test successful.')
                return 'Test successful.', 200
            abort(400)
                
    def run(self):
        if(self.ngrok==True):
            self.start_ngrok()
            self.get_ngrok_ipaddress()
            pprint("Webhook URL = " + str(self.url))
            webhook_api_response=self.id_api.create_webhook(url=self.url)
            pprint("finished create_webhook with api response:")
            pprint(webhook_api_response)
            pprint(webhook_api_response.token)
            self.token=webhook_api_response.token

        #Configure logging
        logging.basicConfig(filename=self.log, level=logging.WARNING)

        self.route_webhook()

        #Start the Flask app
        self.app.run(host='localhost', port=self.port, use_reloader=False)
        self.cleanup()

    def cleanup(self):
        if(self.ngrok_process):
            pprint("Cleaning up...")
            self.ngrok_process.terminate()
            self.tunnel_info_process.terminate()
            self.ngrok_process.wait()
            self.tunnel_info_process.wait()


if __name__ == "__main__":
    from cb_idcheck import webhook
    wh=webhook.webhook()
    wh.parse_args()
    wh.run()
