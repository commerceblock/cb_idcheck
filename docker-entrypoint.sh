#!/bin/bash
echo "52.19.77.60     mongodbhost" >> /etc/hosts
exec "$@"