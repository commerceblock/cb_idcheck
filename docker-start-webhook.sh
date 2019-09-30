#!/bin/bash
docker-compose -p cb-onfido-webhook up -d $@
docker-compose -p cb-onfido-webhook ps
