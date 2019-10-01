#!/bin/bash
IDCHECK_TOKEN=`cat /Users/lawrence/tokens/onfido_api_test`
WEBHOOK_TOKEN=`cat /Users/lawrence/tokens/onfido_webhook_test`
python3 cb_idcheck/webhook.py --token $WEBHOOK_TOKEN --port 59327 --host 127.0.0.1 --log idchecklog.txt --idcheck_token $IDCHECK_TOKEN --id_api onfido --whitelisted_dir=/Users/lawrence/kycfile/whitelisted --consider_dir=/Users/lawrence/kycfile/consider

