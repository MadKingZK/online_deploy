#!/bin/bash
set -e
LOGFILE=/data/django_home/ops/opspro/logs/guni.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=1
TIMEOUT=600

USER=autodep
GROUP=autodep
ADDRESS=127.0.0.1:9905
test -d $LOGDIR || mkdir -p $LOGDIR
exec gunicorn opspro.wsgi:application  -k 'eventlet' -w $NUM_WORKERS --timeout $TIMEOUT --bind=$ADDRESS \
  --user=$USER --group=$GROUP --log-level=debug \
  --log-file=$LOGFILE
