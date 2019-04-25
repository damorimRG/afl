#!/bin/bash

TIME=$1
SLEEP=$2

if [ -z "$1" ]
  then
      echo "No argument supplied"
      exit
fi

if [ -z "$2" ]
  then
      echo "No argument supplied"
      exit
fi

end=$((SECONDS+$TIME))

while [ $SECONDS -lt $end ]; do
    # Do what you want.
    sleep ${SLEEP}s
    echo "time:$SECONDS"
done
