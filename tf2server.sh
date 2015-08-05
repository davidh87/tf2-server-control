#!/bin/bash
#add -x for debug

# Do not change this path
PATH=/bin:/usr/bin:/sbin:/usr/sbin

# User params
ACTION=$1
SERVER=$2
PORT=$3
CONFIG=$4
SCREENNAME=$5

# The path to the game you want to host. example = /home/newuser/dod
DIR=$HOME/servers/$SERVER
DAEMON=$DIR/srcds_run
CONFIG_DIR=$DIR/tf/cfg
DEFAULT_CFG="HLServer"

# Validation
echo $ACTION | grep -E -q '^(start|stop|restart|status)$';
if [ $? -ne 0 ]; then
  echo "Usage: tf2server.sh {start|stop|restart|status} <port> <config>"; 
  exit 0;
fi

echo $PORT | grep -E -q '^[0-9]+$';
if [ $? -ne 0 ]; then
  echo "Port must be numeric, $PORT provided";
  exit 0;
fi

if [ ! -e "$CONFIG_DIR/$CONFIG.cfg" ]; then
  echo "$CONFIG_DIR/$CONFIG.cfg not found - defaulting to $DEFAULT_CFG";
  CONFIG=$DEFAULT_CFG
fi

# Change all PARAMS to your needs.
PARAMS="-game tf +map pl_badwater -port $PORT +exec $CONFIG +sv_pure 2"
NAME=$SCREENNAME:$PORT
DESC="tf2 dedicated server"
# Perform action
case "$1" in
  # Start the server
  start)
    if screen -ls |grep $NAME; then
      echo "Server running: $NAME"
      exit 1
    fi

    echo "Starting $DESC: $NAME"
    if [ -e $DIR ]; then
      cd $DIR
      screen -d -m -S $NAME $DAEMON $PARAMS
    else 
	  echo "No such directory: $DIR!"
    fi
  ;;
  # Stop the server
  stop)
    if screen -ls |grep $NAME; then
      echo -n "Stopping $DESC: $NAME"
      kill `screen -ls |grep $NAME |awk -F . '{print $1}'|awk '{print $1}'`
      echo " ... done."
    else
      echo "Coulnd't find a running $DESC"
    fi
  ;;
  # Restart server
  restart)
    if screen -ls |grep $NAME; then
      echo -n "Stopping $DESC: $NAME"
      kill `screen -ls |grep $NAME |awk -F . '{print $1}'|awk '{print $1}'`
      echo " ... done."
    else
      echo "Couldn't find a running $DESC"
    fi
    
	echo -n "Starting $DESC: $NAME"
    cd $DIR
    screen -d -m -S $NAME $DAEMON $PARAMS
    echo " ... done."
    ;;
  # Check status
  status)
    # Check whether there's a "srcds" process
    ps aux | grep -v grep | grep "$SCREENNAME" > /dev/null
    CHECK=$?
    [ $CHECK -eq 0 ] && echo "SRCDS is UP" || echo "SRCDS is DOWN"
  ;;
  # Default
  *)    
    echo "Usage: $0 {start|stop|status|restart}"
    exit 1
  ;;
esac
exit 0
