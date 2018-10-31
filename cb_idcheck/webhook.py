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
import argparse
import subprocess, sys, time
import smtplib
from email.mime.text import MIMEText

PYTHON=sys.executable
SCRIPT=__file__

class webhook:
    def __init__(self, token=os.environ.get('IDCHECK_WEBHOOK_TOKEN', None), 
                 url=os.environ.get('IDCHECK_WEBHOOK_URL', None), 
                 port=os.environ.get('IDCHECK_WEBHOOK_PORT', None), 
                 log=os.environ.get('IDCHECK_LOG', '/usr/local/var/log/cb_idcheck.log'), 
                 ngrok=False, 
                 idcheck_token=os.environ.get('IDCHECK_API_TOKEN', None),
                 email_password=""):
        self.app = Flask(__name__)
        self.cust_record=record.record()
        self.id_api=cb_onfido.cb_onfido(idcheck_token)
        self.db=database.database()
        self.route='/'
        self.url=url
        self.token=token
        self.log=log
        self.ngrok=ngrok
        self.ngrok_process=None
        self.port=port
        self.email_password=email_password




    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--token', required=False, type=str, help="Webhook token. Default=$IDCHECK_WEBHOOK_TOKEN", default=self.token)
        parser.add_argument('--url', required=False, type=str, help="Webhook token. Default=$IDCHECK_WEBHOOK_URL", default=self.url)
        parser.add_argument('--port', required=False, type=str, help="Webhook token. Default=$IDCHECK_WEBHOOK_PORT", default=self.port)
        parser.add_argument('--log', required=False, type=str, help="Log file. Default=$IDCHECK_LOG", default=self.log)
        parser.add_argument('--idcheck_token', required=False, type=str, help="ID check vendor (e.g. Onfido) API token. Default=$IDCHECK_API_TOKEN", default=self.id_api.token)
        parser.add_argument('--ngrok', required=False, type=bool, help="Bool. Expose local web server to the internet using ngrok?", default=self.ngrok)
        parser.add_argument('--email_password', required=False, type=str, help="Email password.", default=self.email_password)
        args = parser.parse_args(argv)
        self.token = args.token
        self.url=args.url
        self.port=args.port
        self.log=args.log
        self.id_api.set_token(args.idcheck_token)
        self.ngrok=args.ngrok
        self.email_password=args.email_password

    def authenticate(self, request):
        key = urllib.parse.quote_plus(self.token).encode()
        message = request.data
        auth_code=hmac.new(key, message, hashlib.sha1).hexdigest()
        return(auth_code == request.headers["X-Signature"])

    #Expose local web server to the internet (https only)
    def start_ngrok(self):
        self.ngrok_process=subprocess.Popen(["ngrok", "http", "--bind-tls=true", self.port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
    def get_ngrok_tunnel_info(self):
        time.sleep(5)
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

    def send_report(self, applicant_check, subject='no subject'):
        msg=MIMEText(str(applicant_check[0]) + " " + str(applicant_check[1]))
        msg['Subject']=subject
        msg['From']='idcheck@commerceblock.com'
        msg['To']='lawrence@commerceblock.com'
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.login("lawrence@commerceblock.com", self.email_password)
        s.sendmail('idcheck@commerceblock.com', 'lawrence@commerceblock.com', msg.as_string())

    def route_webhook(self):
        @self.app.route(self.route, methods=['POST'])
        def webhook():
            if not self.authenticate(request):
                logging.warning('Python package cb_idcheck.webhook: ' + str(datetime.now()) + ': Message to webhook failed authentication. Request data: ' + request.data.decode("utf-8"))
                abort(401) 
            if(request.json["payload"]["action"]=="check.completed"):
                print('completed check received. applicant id = ' + str(self.cust_record._id))
                applicant_check = self.id_api.find_applicant_check(request.json["payload"]["object"]["href"])
                self.cust_record.import_from_applicant_check(applicant_check)
                if(applicant_check[1].result=="clear"):
                    self.db.addToWhitelist(self.cust_record)
                    print('ID Check result: clear. Added addresses to whitelist.')
                    return 'Added addresses to whitelist.', 200
                #The check returned 'consider' status so human intervention is required.
                elif(applicant_check[1].result=="consider"):
                    print('ID Check result: consider. Addding check to considerlist.')
                    self.db.addToConsiderlist(applicant_check)
                    return 'Added addresses to considerlist.', 200
                #The check returned a failure and will be logged.
                else:
                    print('ID Check result: fail')
            if(request.json["payload"]["action"]=="test_action"):
                print('Test successful.')
                return 'Test successful.', 200
            abort(400)
                
    def run(self):
        if(self.ngrok==True):
            self.start_ngrok()
            self.get_ngrok_ipaddress()
            webhook_api_response=self.id_api.create_webhook(url=self.url)
            self.token=webhook_api_response.token

        #Configure logging
        logging.basicConfig(filename=self.log, level=logging.WARNING)
        #Connect to the whitelist database server
        self.db.connect()

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
