#!/bin/bash -eu
export pidfile="pidfile"
export logfile="log"
export cmd="python3 server.py"
stop() {
  if [ -e $pidfile ]; then
    pid=$(cat $pidfile)
    echo "Stop $cmd"
    kill $pid
    rm -f $pidfile
  else
    echo "Not found $pidfile file"
    false
  fi
}
start() {
  if [ -e $pidfile ]; then
    echo "$pidfile file exists"
    false
  else
    echo "Start $cmd"
    $cmd > $logfile 2>&1 &
    pid=$!
    echo $pid > $pidfile
    disown $pid
    echo "pid: $pid"
  fi
}

arg=${1:-start}
case $arg in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  nod)
    $cmd
    ;;
  *)
  echo "Unknown cmd: $1"
    ;;
esac
