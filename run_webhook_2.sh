#!/bin/bash
python3 cb_idcheck/webhook.py --token NlSoiPwYZaTW-mGPy1eHrhY9Ogrcl1SE --url https://8fa25d27.ngrok.io --port 59327 --log idchecklog.txt --idcheck_token_file /Users/lawrence/tokens/onfido_api_test --id_api onfido --whitelisted_dir=/Users/lawrence/kycfile/whitelisted --consider_dir=/Users/lawrence/kycfile/consider

