FROM tiangolo/uwsgi-nginx-flask:python3.7

ENV LISTEN_PORT 59327

EXPOSE 59327

COPY ./cb_idcheck /app
COPY uswgi.ini /app
COPY prestart.sh /app
COPY . /usr/src/package

RUN set -x \
    && cd /usr/src/package \
    && export FLASK_ENV=development \
    && export IDCHECK_WEBHOOK_TOKEN='snM4YK7nB-KzdJMd25MuoacqLfeuqiOD' \
    && export IDCHECK_API_TOKEN='api_sandbox.TEyAZKULw1v.LiV-4W-BDxAxTKiQoJQNxAu9NO-z_vpd' \
    && export IDCHECK_WEBHOOK_PORT='59327' \
    && export IDCHECK_WEBHOOK_ROUTE='/' \
    && python3 setup.py build \
    && python3 setup.py install \
    && cp depends/ngrok /usr/local/bin \
    && mkdir -p /usr/local/var/log \
    && mkdir -p /storage/kycfile/whitelisted \
    && mkdir -p /storage/kycfile/consider \
    && mkdir -p /run/secrets \
    && echo api_sandbox.TEyAZKULw1v.LiV-4W-BDxAxTKiQoJQNxAu9NO-z_vpd > /run/secrets/onfido_token \
    && echo NlSoiPwYZaTW-mGPy1eHrhY9Ogrcl1SE > /run/secrets/onfido_webhook_token \
    && cp docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
