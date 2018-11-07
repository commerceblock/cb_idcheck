FROM python:3.6.6-stretch

COPY . /usr/src

RUN set -x \
    && cd /usr/src \
    && python setup.py build \
    && python setup.py install \
    && cp depends/ngrok /usr/local/bin \
    && mkdir -p /usr/local/var/log \
    && cp docker-entrypoint.sh ../../

ENTRYPOINT ["/docker-entrypoint.sh"]
