#!/bin/bash
set -e

if [ -f /run/secrets/onfido_token ] && [ -f /run/secrets/onfido_webhook_token ]; then
    creds=("--idcheck_token=$(cat /run/secrets/onfido_token)" "--token=$(cat /run/secrets/onfido_webhook_token)")
fi

cd /usr/src/package/cb_idcheck

exec "$@" "${creds[@]}"
