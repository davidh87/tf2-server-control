#!/usr/bin/python

import argparse
import sys
import re
import os
import shutil
import yaml
from zipfile import ZipFile
from bz2 import BZ2File
from commands import *
from SourceQuery import SourceQuery;

configs = {}

def main() :
  global configs
  stream = open(sys.path[0]+"/servers.yaml", 'r')
  configs = yaml.load(stream)
  
  parser = argparse.ArgumentParser(description='Control tf2 servers')
  
  parser.add_argument('--update', nargs='+', metavar='directory', help='Update TF2 installation binaries')
  parser.add_argument('--install', metavar='directory', help='Install tf2 binaries')
  parser.add_argument('--status', nargs='+', metavar='servername', help='Get status of TF2 server')
  parser.add_argument('--start', nargs='+', metavar='servername', help='Start TF2 server')
  parser.add_argument('--restart', nargs='+', metavar='servername', help='Forcefully restart TF2 server')
  parser.add_argument('--restartall', action='store_true', help='Forcefully restart all running TF2 servers')
  parser.add_argument('--stop', nargs='+', metavar='servername', help='Stop TF2 server')
  parser.add_argument('--updateconfigs', nargs=2, metavar=('serverdir','zipfile'), help='Update config files')
  parser.add_argument('--deploymap', nargs='+', metavar='filename', help='Deploy a map to all server installs')
  parser.add_argument('--checkrestart', action='store_true', help='Check if servers need restarting, and restart if needed')
  parser.add_argument('--running', action='store_true', help='Get running server names')
  
  args = parser.parse_args()

  
  if args.updateconfigs :
    updateConfigs(args.updateconfigs[0], args.updateconfigs[1])
  if args.deploymap :
    deployMap(args.deploymap)
  if args.install :
    installServer(args.install)
  if args.update :
    updateServers(args.update)
  if args.status :
    serverStatus(args.status)
  if args.start :
    startServer(args.start)
  if args.restart :
    restartServer(args.restart)
  if args.restartall :
    restartServer(getRunningServerNames());
  if args.stop :
    stopServer(args.stop)
  if args.checkrestart :
    checkRestart()
  if args.running:
    print getRunningServerNames()
    
def getConfigDetails( servername ) :
  server = configs[servername]
  return server

def updateServers( serverdirs ) :
  #Screen format: $CONFIG:$PORT
  
  for serverdir in serverdirs:
    updateServer (serverdir)

def updateServer( serverdir ) :
  fullserverdir = getFullServerDir(serverdir)
  
  if os.path.isdir(fullserverdir) == False:
    print "Serverdir %s does not exist. Use 'install' rather than 'update' to deploy a new server dir" % (fullserverdir)
    return;
 
  status, text = getstatusoutput("$HOME/steamcmd.sh +login anonymous +force_install_dir %s +app_update 232250 validate +quit" % (fullserverdir))

  for line in text.splitlines():
    if line == "":
      continue;

    m = re.search('Success! App \'232250\' fully installed\.', line)
    if m == None:
      continue;

    print "Update found..."

    # It matched
    status, screens = getstatusoutput("screen -ls")
    for screen in screens.splitlines():
      matchobj = re.search('(?<=\.)([a-zA-Z0-9\-]+):([0-9]+)', screen)
      if matchobj == None:
        continue
      cfg = matchobj.group(1)
      port = matchobj.group(2)

      print "Marking server as needing restart - %s:%s" % (cfg,port)
      os.system("echo restart > $HOME/tmp/%s-%s.server" % (cfg, port))
        
    print "Finished updating"
    return
  print "No update found for server %s" % (serverdir)
    
def installServer( serverdir ) :
  fullserverdir = getFullServerDir(serverdir)
  
  if os.path.isdir(fullserverdir) == True:
    print "Serverdir %s already exists. Use 'update' rather than 'install' to update a new server dir" % (fullserverdir)
    return
  
  os.system("$HOME/steamcmd.sh +login anonymous +force_install_dir %s +app_update 232250 validate +quit" % (fullserverdir))
  
def startServer( servernames ) :
  for servername in servernames:
    serverdetails = getConfigDetails(servername)
    server = serverdetails['server']
    port = serverdetails['port']
    cfg = serverdetails['cfg']
    os.system('$HOME/.scripts/tf2-scripts/tf2server.sh start %s %s %s %s' % (server, port, cfg, servername))

def stopServer( servernames ) :
  for servername in servernames:
    serverdetails = getConfigDetails(servername)
    server = serverdetails['server']
    port = serverdetails['port']
    cfg = serverdetails['cfg']
    os.system('$HOME/.scripts/tf2-scripts/tf2server.sh stop %s %s %s %s' % (server, port, cfg, servername))

def serverStatus( servernames ) :
  for servername in servernames:
    serverdetails = getConfigDetails(servername)
    server = serverdetails['server']
    port = serverdetails['port']
    cfg = serverdetails['cfg']
    os.system('$HOME/.scripts/tf2-scripts/tf2server.sh status %s %s %s %s' % (server, port, cfg, servername))

def restartServer( servernames ) :
  for servername in servernames:
    serverdetails = getConfigDetails(servername)
    server = serverdetails['server']
    port = serverdetails['port']
    cfg = serverdetails['cfg']
    os.system('$HOME/.scripts/tf2-scripts/tf2server.sh restart %s %s %s %s' % (server, port, cfg, servername))

def getFullServerDir( serverdir ) :
  homedir = os.path.expanduser("~")
  fullserverdir = "%s/servers/%s" % (homedir, serverdir)
  
  return fullserverdir  

def updateConfigs( serverdir, zippath) :
  if serverdir == 'all': 
    servers = set([configs[key]['server'] for key in configs])
  else:
    servers = [serverdir]
  
  for server in servers:
    fullserverdir = getFullServerDir(server)
  
    if os.path.isdir(fullserverdir) == False:
      print "Server %s does not exist." % (fullserverdir)
      continue

    if os.path.exists(zippath) == False:
      print "Zip file %s does not exist" % (zippath)
      continue
    
    print "Extracting zip for server %s" % (server)
    zipfile = ZipFile(zippath, 'r')
    zipfile.extractall("%s/tf/cfg/" % (fullserverdir))

def deployMap( mappaths ) :
  servers = set([configs[key]['server'] for key in configs])
  
  for serverdir in servers :
    fullserverdir = getFullServerDir(serverdir)
  
    if os.path.isdir(fullserverdir) == False:
      print "Serverdir %s does not exist." % (fullserverdir)
      return
   
    for mappath in mappaths: 
      if os.path.exists(mappath) == False:
        print "Map file %s does not exist" % (mappath)
  
      mapname = os.path.basename(mappath)
      outputpath = "%s/tf/maps/%s" % (fullserverdir, mapname)
  
      if os.path.exists(outputpath) :
        print "Map already exists at %s" % (outputpath)
        continue
        
      print "Copying map %s to %s" % (mapname, outputpath)  
      shutil.copy(mappath, outputpath)

def getRunningServerNames():
  servernames = []
  
  status, screens = getstatusoutput("screen -ls")
  for screen in screens.splitlines():
    matchobj = re.search('(?<=\.)([a-zA-Z0-9\-]+):([0-9]+)', screen)
    if matchobj == None:
	    continue
    tmp_servername = matchobj.group(1)
    servernames.append(tmp_servername)
  return servernames
      
def checkRestart() :
  status, home = getstatusoutput("echo $HOME")
  
  server = "confusedherring.com"
  
  dir = home + "/tmp/"
  files = os.listdir(dir)
  runningServers = getRunningServerNames()

  for file in files:
    print "file: %s" % file
    f = open(dir + file, 'r');
    cmd = f.readline().strip();
    matchobj = re.search('([a-zA-Z0-9\-]+)-(\d+)\.server', file)
    if matchobj == None:
      continue;  
    servername = matchobj.group(1);

    server_running = 0
    #except: wasnt working, so do it the long way
    
    for tmp_servername in runningServers:
      if servername == tmp_servername:
        server_running = 1;
        break;
	
    if server_running == 1:
      serverDetails = getConfigDetails(servername)
      query = SourceQuery(server, int(serverDetails['port']))
      sinfo = query.info();
      if int(sinfo['numplayers']) <= 1:
        print "1 or less";
        restartServer([servername])
        os.system("rm " + dir + file);
    else:
      startServer([servername])
      os.system("rm " + dir + file);
        
main()
