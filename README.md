# cb_idcheck

Tools for managing a whitelisting database for a Ocean (https://github.com/commerceblock/ocean) sidechain.

## Installation

    $ python3 setup.py build && python3 setup.py install


## Overview 

### Main modules

- idcheck - a user details submission GUI for Onfido ID checks.
- webhook - webhook monitoring daemon for changes returned from Onfido following submission of an ID check.
- watch - daemon for updating the local node whitelist in response to changes to a mongodb database.
- process_considerlist - a script to assist with processing uses that have not passes all KYC checks.
- database - mongodb whitelisting database client (derpricated).


### Basic usage

- Optional: run webhook.py. For testing purposes, a temporary webhook can be set up using the --ngrok=true option. The KYC provider API configuration must be provided - run with the --help argument for more details.

- Submit user details to the KYC provider using idcheck.py. This be done using the test GUI or by providing the required data as command line arguments.

On receipt of the check results, webhook.py will write a ID tagged and timestamped KYC file into either the 'whitelisted' or 'consider' directory depending on the outcome of the checks. 

Additional scripts are supplied to automaticically whitelist addresses on receipt of the whitelisted user data (KYC file), and for processing users that have not passed all checks: these are watch.py and process_considerlist.py.

## Modules

### idcheck

For sumbitting customer ID details to the idcheck vendor (e.g. Onfido). This can be run either as a command or as a GUI. To run the GUI:

Run:


    $ python3 idcheck.py --gui true


An ID check can also be requested in a single command. See help for details:  


    $ python3 idcheck.py --help


Finally, the class "idcheck" can be imported into another python script:  


    from cb_idcheck.idcheck import idcheck  
    idc=idcheck()  
    idc.first_name="Tom"  
    ...  
    idc.submit()  




### webhook

A client that monitors a webhook for updates from the id check vendor (e.g. Onfido) and saves the whitelist KYC files to a directory for subsequent user onboarding. The default directories are 'whitelisted' for whitelisted KYC files belonging to users that passed all checks, and 'consider' for KYC files that belong to users who fell short of passing all checks.

#### Open and register a new webhook

If the argument --ngrok True is passed then the client will:  
   - create a https tunnel from the the local host to the internet using ngrok 
   - use the url established by ngrok to register a new webhook with the ID check vendor and import the authentication token
   - begin monitoring the above webhook for new ID check results or updates

Example 


    $ python3 webhook.py --ngrok True

#### Monitor an existing webhook

To begin monitoring an existing webhook:
	      
    $ python3 webhook.py --token $IDCHECK_WEBHOOK_TOKEN --public_url $IDCHECK_WEBHOOK_URL \  
      --port $IDCHECK_WEBHOOK_PORT --log $IDCHECK_LOG --public_url $IDCHECK_WEBHOOK_URL \  
      --ngrok False  
  
Defaults:  
- token: $IDCHECK_WEBHOOK_TOKEN - the webhook authentication token supplied by the idcheck vendor when registering the webhook.  
- port: $IDCHECK_WEBHOOK_PORT   
- url: $IDCHECK_WEBHOOK_URL   
- log: $IDCHECK_LOG if it exists, otherwise '/usr/local/var/log/cb_idcheck.log' - webhook access/authentication log.  
- ngrok: False  


### watch
A client to update a node whitelist with additions and updates to the the mongdb whitelist database.

To start the client:

   
    $ python3 watch.py --rpcconnect $HOST --rpcport $PORT --rpcuser $USER --rpcpassword $PASS \  
    --dbuser $MONGODB_USER --dbpassword $MONGODB_PASS  
  
Defaults:  
- rpcconnect: $HOST - the ip address of the whitelist node.  
- rpcport: $PORT - the port of the whitelist node RPC server.  
- rpcuser: $USER  
- rpcpassword: $PASS - the user name and password for the above (see the .conf file in the node data dir).  
- dbuser: $MONGODB_USER  
- dbpassword: $MONGODB_PASS - mongodb whitelist database user name and password.  

### process_considerlist

The result of some kyc checks is 'consider' due to e.g. missing information or adverse media. When this occurs, the details are added to a considerlist container in the same database as the whitelist container.
This interactive script can be used to review the entries in the consider list and either accept or reject them for whitelisting.

Example


    $ python3 process_considerlist.py --username $USERNAME --password $PASSWORD --port $PORT \  
      --host $HOSTS --authsource $AUTHSOURCE --authmechanism $AUTHMECHANISM --idcheck_token \  
      $IDCHECK_API_TOKEN  	


Defaults:  
- username: $MONGODB_USER  
- password: $MONGODB_PASS  
- port: $MONGODB_PORT  
- host: mongodbhost (defined in /etc/hosts)  
- authsource: $MONGODB_USER  
- authmechanism: 'SCRAM-SHA-256'  
- idcheck_token: $IDCHECK_API_TOKEN  

### database

Interface to the whitelisting database.

To run the test:


    $ python3 -m database --username $USERNAME --password $PASSWORD --port $PORT --host $HOSTS \  
      --authsource $AUTHSOURCE --authmechanism $AUTHMECHANISM  
	
Defaults:  
-username: $MONGODB_USER  
-password: $MONGODB_PASS  
-port: $MONGODB_PORT  
-host: mongodbhost (defined in /etc/hosts)  
-authsource: $MONGODB_USER  
-authmechanism: 'SCRAM-SHA-256'  


Example use: see database.test() in database.py 
