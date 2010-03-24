#!/usr/bin/env python
from ab2pt import adapt

def debug_output(obj):
	for r in ab2pt.records:
		for (k,v) in r.items():
			print >>stderr, (k+":").ljust(15), v
		print >>stderr, "--"

if __name__ == "__main__":
	from sys import argv, stderr, stdout
	if(len(argv) < 2):
		print "Usage: %s [ab-user-stories.csv]" % argv[0]
		exit(1)
	ab2pt = adapt( open(argv[1],"rU") )
	ab2pt.write_csv(stdout)
	
	#debug_output(ab2pt)
