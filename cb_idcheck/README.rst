##########
cb_idcheck
##########

*********
Overview
*********

Tools for managing a whitelisting database for a Ocean (https://github.com/commerceblock/ocean) sidechain.

The main classes of interest are:

#. idcheck - a user details submission GUI for Onfido ID checks.
#. database - for interacting with a mongodb whitelisting database.
#. webhook - for monitoring a webhook for changes returned from Onfido following submission of an ID check.
#. watch - for updating the local node whitelist in response to changes to a mongodb database.

********
Modules
********

idcheck
________

Run::

	>>> python idcheck.py


database
________

To run a test::

	>>> python database.py

webhook
________

Monitor the chosen webhook for updates from Onfido.

To run the example::

	>>> python webhook.py




