#!/bin/bash


# TO USE: ln -s /opt/tools/jstack_collector/run.sh /etc/cron.hourly/

# ref: http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd $DIR


## env vars

## scoped only to this run
#export automatic=True

## exec
/usr/bin/env python jstack_collector.py automatic
#/usr/bin/env python jstack_collector.py
