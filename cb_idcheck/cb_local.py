# Copyright (c) 2018 The CommerceBlock Developers                                                                                                              
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

#Local trusted webhook request processing
import os
from .record import record 
from pprint import pprint
from cb_idcheck import record
from flask import request
from werkzeug.utils import secure_filename

class cb_local:
      #'Local' API has no token
      def set_token(self, token=None):
            self.token=None

      def __init__(self, token=None):
            self.record = record()
            self.set_token()
            self.UPLOAD_DIR="/Users/lawrence/wl/whitelisted"
      
            
      def process_webhook_request(self, request):
            files=request.files
            check_id=request.json["payload"]["object"]["check_id"]
            applicant_id=request.json["payload"]["object"]["applicant_id"]
            checkresult=request.json["payload"]["object"]["checkresult"]
            
            if(checkresult=="clear"):
                  nfiles_valid=1
                  if len(files) != nfiles_valid:
                        error_message = "Error: bad_request for checkid " + checkid + ": expected " + str(nfilesvalid) + " files, got " + str(len(files))
                        return error_message, 400

            file = files[0]
            if file:
                  #Check the file name
                  filename = self.UPLOAD_DIR+ "/" + applicant_id + "/" + check_id + "/kycfile_" + applicant_id + "_" + check_id + ".dat"
                  
                        
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

if __name__ == "__main__":
      from cb_idcheck import cb_local
      cb_local.cb_local().test()

