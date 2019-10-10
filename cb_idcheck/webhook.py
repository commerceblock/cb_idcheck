# Copyright (c) 2018 TAhe CommerceBlock Developers                                                                                                
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.  

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
import ssl
from string import Template
from email.mime.text import MIMEText
from cb_idcheck.idcheck import idcheck
from cb_idcheck.idcheck_config import idcheck_config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

PYTHON=sys.executable
SCRIPT=__file__

if 'app' not in globals():
    app=Flask(__name__)

class webhook:
    def __init__(self, token=os.environ.get('IDCHECK_WEBHOOK_TOKEN', None), 
                 url=os.environ.get('IDCHECK_WEBHOOK_URL', None), 
                 port=os.environ.get('IDCHECK_WEBHOOK_PORT', None), 
                 log=os.environ.get('IDCHECK_LOG', '/usr/local/var/log/cb_idcheck.log'),
                 host=os.environ.get('IDCHECK_HOST', 'localhost'),
                 id_api=os.environ.get('ID_API', 'onfido'), 
                 ngrok=False, 
                 idcheck_token=os.environ.get('IDCHECK_API_TOKEN', None),
                 whitelisted_dir=os.environ.get('WHITELISTED_DIR', None),
                 consider_dir=os.environ.get('CONSIDER_DIR', None),
                 smtp_conf=None):
        ssl.create_default_context()
        self.idcheck_token=idcheck_token
        self.route='/'
        self.url=url
        self.token=token
        self.log=log
        self.ngrok=ngrok
        self.ngrok_process=None
        self.port=port
        self.host=host
        self.id_api_type=id_api
        self.whitelisted_dir=whitelisted_dir
        self.consider_dir=consider_dir
        self.smtp_conf=smtp_conf
        
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
        parser.add_argument('--whitelisted_dir', required=False, type=str, help="Directory to save the whitelisted kycfiles to. Default=/storage/kycfile/whitelisted", default="/storage/kycfile/whitelisted")
        parser.add_argument('--consider_dir', required=False, type=str, help="Directory to save the considerlisted kycfiles to. Default=/storage/kycfile/consider", default="/storage/kycfile/consider")
        parser.add_argument('--smtp_username_file', required=False, type=str, help="File containing the SMTP username.", default=None)
        parser.add_argument('--smtp_password_file', required=False, type=str, help="File containing the SMTP password.", default=None)
        parser.add_argument('--smtp_server', required=False, type=str, help="SMTP server", default=None)
        parser.add_argument('--smtp_port', required=False, type=str, help="SMTP port", default=None)
        parser.add_argument('--email_from', required=False, type=str, help="The FROM email address", default=None)
        parser.add_argument('--email_subject', required=False, type=str, help="The email subject", default=None)
        parser.add_argument('--email_template_file', required=False, type=str, help="The idcheck completion email template", default=None)
        parser.add_argument('--email_fail_template_file', required=False, type=str, help="The idcheck fail email template", default=None)

        args = parser.parse_args(argv)
        self.whitelisted_dir=args.whitelisted_dir
        self.consider_dir=args.consider_dir
        self.token = args.token
        self.url=args.url
        self.port=args.port
        self.log=args.log
        self.idcheck_token=args.idcheck_token
        self.ngrok=args.ngrok
        self.host=args.host
        self.id_api_type=args.id_api
        #SMTP email config

        if self.smtp_conf == None:
            self.smtp_conf={}
        p=args.smtp_username_file
        if os.path.exists(p):
            with open(p) as f:
                self.smtp_conf["username"]=f.readline().rstrip()
        else:
            self.smtp_conf["username"]=None

        p=args.smtp_password_file
        if os.path.exists(p):
            with open(p) as f:
                self.smtp_conf["password"]=f.readline().rstrip()
        else:
            self.smtp_conf["password"]=None

        p=args.email_template_file
        if os.path.exists(p):
            with open(p) as f:
                self.smtp_conf["complete_template"]=Template(f.read())
        else:
            self.smtp_conf["compete_template"]=None

        p=args.email_fail_template_file
        if os.path.exists(p):
            with open(p) as f:
                self.smtp_conf["fail_template"]=Template(f.read())
        else:
            self.smtp_conf["fail_template"]=None
            
            
        self.smtp_conf["server"]=args.smtp_server
        self.smtp_conf["port"]=args.smtp_port
        self.smtp_conf["email_from"]=args.email_from
        self.smtp_conf["email_subject"]=args.email_subject

        bSMTP=True
        for item in self.smtp_conf:
            if item == None:
                bSMTP=False
                break
        if bSMTP == False:
            self.smtp_conf=None
   
    def authenticate(self, req):
        key = urllib.parse.quote_plus(self.token).encode()
        message = req.data
        auth_code=hmac.new(key, message, hashlib.sha256).hexdigest()
        return(auth_code == req.headers["X-Sha2-Signature"])

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
        for report_req in self.idcheck_config.check.reports:
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

    def hello(self):
        return "Hello World from cb_idcheck webhook class"

    def process_post(self, req):
        if not self.authenticate(req):
            logging.warning('cb_idcheck.webhook: ' + str(datetime.now()) + ': A request sent to the webhook failed authentication.')
            abort(401)
        if(req.json["payload"]["action"]=="check.completed"):
            print('completed check received')
            report_list=self.id_api.list_reports(req.json["payload"]["object"]["id"])
            if(self.verify_check_content(report_list) == False):
                infostr='ID Check result: check does not contain all the required report types. The required report types are: ' + str(self.idcheck_config) +  '. The included report types are: '
                print(infostr)
                logging.info('%s', infostr)
                pprint(report_list)
                self.send_fail_email()
                return infostr, 200
            else:
                message, retval = self.id_api.process_webhook_request(req)
                if retval != None:
                    print(message)
                    logging.info('%s', message)
                    self.send_confirmation_email()
                    return message, retval
                else:
                    if message == None:
                        message="Check failed. check-id: " + str(self.id_api.get_checkid_from_request(req))
                    logging.info('%s', message)
                    print(message)
                    self.send_fail_email()
                    return message, 200
        elif(req.json["payload"]["action"]=="check.started"):
            infostr="Check started. check-id: " + str(self.id_api.get_checkid_from_request(req))
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="check.reopened"):
            infostr="Check reopened. check-id: " + str(self.id_api.get_checkid_from_request(req))
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="check.withdrawn"):
            infostr="Check withdrawn. check-id: " + str(self.id_api.get_checkid_from_request(req))
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="check.form_opened"):
            infostr="Check form opened. check-id: " + str(self.id_api.get_checkid_from_request(req))
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="check.form_completed"):
            infostr="Check form completed. check-id: " + str(self.id_api.get_checkid_from_request(req))
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="report.withdrawn"):
            infostr="Report withdrawn"
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="report.resumed"):
            infostr="Report resumed"
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="report.cancelled"):
            infostr="Report cancelled"
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="report.awaiting_approval"):
            infostr="Report awaiting approval"
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200

        elif(req.json["payload"]["action"]=="report.completed"):
            infostr="Report completed"
            print(infostr)
            logging.info('%s', infostr)
            return infostr, 200
        
        elif(req.json["payload"]["action"]=="test_action"):
            infostr='Test successful.'
            print(infostr)
            print('Test successful.')
            logging.info('%s', infostr)
            return infostr, 200
        logging.info('Unable to process request: %s', req.json)
        print("Unable to process request: {}".format(req.json))
        return "Unable to process request: {}".format(req.json), 400

    def send_confirmation_email(self):
        if self.smtp_conf == None:
            return
        self.send_email(self.smtp_conf["complete_template"])

    def send_fail_email(self):
        if self.smtp_conf == None:
            return
        self.send_email(self.smtp_conf["fail_template"])
        
    def send_email(self, template):
        if self.smtp_conf == None:
            return
        full_name=str(self.id_api.record.first_name) + " " + str(self.id_api.record.last_name)        
        msg = MIMEMultipart()       # create a message
        message = template.substitute(TO_NAME=full_name)
        msg['From']=self.smtp_conf["email_from"]
        msg['To']=self.id_api.record.email
        msg['Subject']=self.smtp_conf["email_subject"]
        msg.attach(MIMEText(message, 'plain'))
        try:
            s = smtplib.SMTP_SSL(host='email-smtp.eu-west-1.amazonaws.com', port=465)
            s.login(self.smtp_conf["username"], self.smtp_conf["password"])
            s.send_message(msg)
        except Exception as e:
            print(e)
            logging.error('cb_idcheck.webhook.send_email: ' + str(datetime.now()) + ' ' + str(e))
            
        del msg
    
    def route_webhook(self):
        @app.route("/")
        def hello():
            return self.hello()

        
        @app.route(self.route, methods=['POST'])
        def webhook():
            return self.process_post(request)

    def init(self):
        if self.id_api_type == str("onfido"):
            self.id_api = cb_onfido.cb_onfido(token=self.idcheck_token, whitelisted_dir=self.whitelisted_dir, consider_dir=self.consider_dir)
            self.idcheck_config=idcheck_config(self.id_api.onfido.Check(type='express'))
        elif self.id_api_type == str("local"):
            selfid_api = cb_local.cb_local()
        else:
            sys.exit("Error: unknown id_api: " + args.id_api)
        
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
        logging.basicConfig(filename=self.log, level=logging.INFO)


    #Start the Flask app
    def run(self):
        self.route_webhook()
        app.run(host=self.host, port=self.port, use_reloader=False)
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
    wh.init()
    wh.run()

