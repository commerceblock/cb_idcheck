# Copyright (c) 2018 The CommerceBlock Developers                                                                                                              
# Distributed under the MIT software license, see the accompanying                                                                                             # file LICENSE or http://www.opensource.org/licenses/mit-license.php.  

import argparse
from cb_idcheck.cb_onfido import cb_onfido

class idcheck_config:
    def __init__(self,check):
        self.check=check
        self.check.type='express'
        onf=cb_onfido()
        #Fill the reports list with the required reports
        self.check.reports=[]
        self.check.reports.append(onf.onfido.Report())
        self.check.reports[-1].name='document'
        self.check.reports.append(onf.onfido.Report())
        self.check.reports[-1].name='facial_similarity'
        self.check.reports[-1].variant='standard'
#        self.check.reports.append(onf.onfido.Report())
#        self.check.reports[-1].name='identity'
#        self.check.reports[-1].variant='kyc'
        self.check.reports.append(onf.onfido.Report())
        self.check.reports[-1].name='watchlist'
        self.check.reports[-1].variant='kyc'

    def __str__(self):
        result=""
        nRep=0
        for report in self.check.reports:
            nRep = nRep+1
            result = result + ' ' + str(nRep) + ': '
            if(report.name != None):
                result = result + ' name: ' + report.name 
                if(report.variant != None):    
                    result = result + ' variant: ' + report.variant
                else:
                    result = result + ' variant: ' + 'standard'
        return result
    
