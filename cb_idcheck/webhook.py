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
import subprocess
import time

class webhook:
    def __init__(self, route='/', token=None, port=None, logfile=None):
        self.app = Flask(__name__)
        self.cust_record=record.record()
        self.id_api=cb_onfido.cb_onfido()
        self.db=database.database()
        self.route=route
        self.token=token
        self.logfile=logfile

    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--token', required=False, type=str, help="Webhook token. Default=$CB_IDCHECK_WEBHOOK_TOKEN", default=os.environ.get('CB_IDCHECK_WEBHOOK_TOKEN', None))
        parser.add_argument('--port', required=False, type=str, help="Webhook token. Default=$CB_IDCHECK_WEBHOOK_PORT", default=os.environ.get('CB_IDCHECK_WEBHOOK_PORT', None))
        parser.add_argument('--route', required=False, type=str, help="Webhook token. Default=$CB_IDCHECK_WEBHOOK_ROUTE", default=os.environ.get('CB_IDCHECK_WEBHOOK_ROUTE', '/'))
        parser.add_argument('--logfile', required=False, type=str, help="Log file. Default=$CB_IDCHECK_LOG", default=os.environ.get('CB_IDCHECK_LOG', '/usr/local/var/log/cb_idcheck.log'))
        parser.add_argument('--ngrok', required=False, type=bool, help="Bool. Expose local web server to internet using ngrok? (This is for testing purposes only).", default=False)
        args = parser.parse_args(argv)
        self.token = args.token
        self.port=args.port
        self.route=args.route
        self.logfile=args.logfile
        self.ngrok=args.ngrok

    def authenticate(self, request):
        key = urllib.parse.quote_plus(self.token).encode()
        message = request.data
        auth_code=hmac.new(key, message, hashlib.sha1).hexdigest()
        return(auth_code == request.headers["X-Signature"])

    #Expose local web server to the internet (https only)
    def start_ngrok(self):
#        subprocess.Popen(["nohup", "ngrok", "http", "--bind-tls=true", self.port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.Popen(["ngrok", "http", "--bind-tls=true", self.port], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
    def get_ngrok_tunnel_info(self):
        p = subprocess.Popen(["curl", "http://127.0.0.1:4040/api/tunnels", "--connect-timeout", "10"], stdout=subprocess.PIPE)        
        self.tunnel_info=json.loads(p.communicate()[0].decode("UTF-8"))
        print(self.tunnel_info)
        return self.tunnel_info
        
    def get_ngrok_ipaddress(self):
        self.get_ngrok_tunnel_info()
        self.ngrok_public_url=self.tunnel_info['tunnels'][0]['public_url']
        print("Webhook i.p. address: " + self.ngrok_public_url)
        print("route: " + self.route)
        return self.ngrok_public_url

    def route_webhook(self):
        @self.app.route(self.route, methods=['POST'])
        def webhook():
            print('webhook received')
            if not self.authenticate(request):
                logging.warning('Python package cb_idcheck.webhook: ' + str(datetime.now()) + ': Message to webhook failed authentication. Request data: ' + request.data.decode("utf-8"))
                abort(401) 
            if(request.json["payload"]["action"]=="check.completed"):
                applicant_check = self.id_api.find_applicant_check(request.json["payload"]["object"]["href"])
                if(applicant_check[1].result=="clear"):
                    self.cust_record.import_from_applicant_check(applicant_check)
                    self.db.addToWhitelist(self.cust_record)
                    return 'Added addresses to whitelist.', 200
            if(request.json["payload"]["action"]=="test_action"):
                print('Test successful.')
                return 'Test successful.', 200
            abort(400)
                
    def run(self):
        if(self.ngrok==True):
            self.start_ngrok()
            self.get_ngrok_ipaddress()
            print("Register the above webhook I.P. address with the identity check provider and obtain the authentication token.")
            self.token=input("Webhook authentication token: ")
            
        #Configure logging
        logging.basicConfig(filename=self.logfile, level=logging.WARNING)
        #Connect to the whitelist database server
        self.db.connect()

        self.route_webhook()

        #Start the Flask app
        self.app.run(host='localhost', port=self.port, use_reloader=False)


if __name__ == "__main__":
    from cb_idcheck import webhook
    wh=webhook.webhook()
    wh.parse_args()
    wh.run()
