# cb_idcheck

Tools for managing a whitelisting database for a Ocean (https://github.com/commerceblock/ocean) sidechain.

## Installation
   `python3 setup.py build && python3 setup.py install`


## Overview

Main modules:

#. idcheck - a user details submission GUI for Onfido ID checks.
#. database - mongodb whitelisting database client.
#. webhook - webhook monitoring daemon for changes returned from Onfido following submission of an ID check.
#. watch - daemon for updating the local node whitelist in response to changes to a mongodb database.

## Modules

### idcheck

A GUI for sumbitting customer ID details to the idcheck vendor (e.g. Onfido).

Run::

	>>> python idcheck.py


### database

Interface to the whitelisting database.

To run the test:

`python3 -m database --username $USERNAME --password $PASSWORD --port $PORT --host $HOSTS --authsource $AUTHSOURCE --authmechanism $AUTHMECHANISM`	
	
Defaults:
-username: $MONGODB_USER
-password: $MONGODB_PASS
-port: $MONGODB_PORT
-host: mongodbhost (defined in /etc/hosts)
-authsource: $MONGODB_USER
-authmechanism: 'SCRAM-SHA-256'

Example use: see database.test() in database.py 

### webhook

A client that monitors a webhook for updates from the id check vendor (e.g. Onfido) and publishes the whitelisted keys to a mongdb database.

#### Open and register a new webhook

If the argument --ngrok True is passed then the client will:
   - create a https tunnel from the the local host to the internet using ngrok 
   - use the url established by ngrok to register a new webhook with the ID check vendor and import the authentication token
   - begin monitoring the above webhook for new ID check results or updates

Example ::

	>>> python webhook.py --ngrok True

Note: the webhook tunnel (ngrok process) will be closed when the program exists normally e.g. receives the SIGINT (Ctrl-C) or SIGTERM signal. However, 
if the webhook.py process is terminated with the KILL signal then the ngrok process will have to be terminated manually, e.g.

        >>> ps ux | grep ngrok
	>>> kill <ngrok PID>

#### Monitor an existing webhook

To begin monitoring an existing webhook:
	      
	>>> python webhook.py --token $IDCHECK_WEBHOOK_TOKEN --public_url $IDCHECK_WEBHOOK_URL --port $IDCHECK_WEBHOOK_PORT --log $IDCHECK_LOG --public_url $IDCHECK_WEBHOOK_URL --ngrok False

	Defaults:
	-token: $IDCHECK_WEBHOOK_TOKEN - the webhook authentication token supplied by the idcheck vendor when registering the webhook.
	-port: $IDCHECK_WEBHOOK_PORT 
	-url: $IDCHECK_WEBHOOK_URL 
	-log: $IDCHECK_LOG if it exists, otherwise '/usr/local/var/log/cb_idcheck.log' - webhook access/authentication log.
	-ngrok: False

### watch
A client to update a node whitelist with additions and updates to the the mongdb whitelist database.

To start the client:
   
	>>> python watch.py --rpcconnect $HOST --rpcport $PORT --rpcuser $USER --rpcpassword $PASS --dbuser $MONGODB_USER --dbpassword $MONGODB_PASS

	Defaults:
	-rpcconnect: $HOST - the ip address of the whitelist node. 
	-rpcport: $PORT - the port of the whitelist node RPC server.
	-rpcuser: $USER  
	-rpcpassword: $PASS - the user name and password for the above (see the .conf file in the node data dir). 
	-dbuser: $MONGODB_USER 
	-dbpassword: $MONGODB_PASS - mongodb whitelist database user name and password.
