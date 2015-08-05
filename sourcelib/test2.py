from SourceQuery import SourceQuery
import sys

def main(args):
    qryr = SourceQuery(args[0], int(args[1]))
    
    sinfo = qryr.info()
    splayer = sorted(qryr.player(), key=lambda p: p['kills'], reverse=True)
    srules = qryr.rules()
    
    print sinfo['hostname']
    print '*' * len(sinfo['hostname'])
    print
    
    print "(" + ("Linux" if sinfo['os'] == 'l' else "Windows") + " server, version " + str(sinfo['version']) + (", passworded" if sinfo['passworded'] == 1 else ', unpassworded') + ")"
    print
    
    print str(sinfo['numplayers']) + " of " + str(sinfo['maxplayers']) + " players mooching about:"
    
    for p in splayer:
        pname = "<unnamed>" if p['name'] == "" else p['name']
        print " - " + pname + " (" + str(p['kills']) + " kills" + (" as they suck at this game" if p['kills'] == 0 else "") + ", connected for " + str(int(p['time'])) + "s)"
	
    print
    
    print "Current map is " + sinfo['map'] + ". Next is currently " + srules['sm_nextmap'] + "." + ("Learning through repetition!" if sinfo['map'] == srules['sm_nextmap'] else "")
    print
    
    print "Gravity is currently " + srules['sv_gravity']
    print
	
if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "usage: " + sys.argv[0] + " host port"
		sys.exit(1)
	
	main(sys.argv[1:])
