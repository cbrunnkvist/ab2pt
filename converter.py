#!/usr/bin/env python
from ab2pt import adapt

######################################
if __name__ == "__main__":
	from sys import argv, stderr, stdout
	if(len(argv) < 2):
		print "Usage: %s [ab-user-stories.csv]" % argv[0]
		exit(1)
	ab2pt = adapt( open(argv[1],"rU") )
	ab2pt.write_csv(stdout)
	#for record in ab2pt.records:
	#	print "%(Id)s: %(Accepted at)s (%(Current State)s)" % (record)
	#	pass
#	for n in range(-12,-7):
	for n in range(6,9):
		for (k,v) in ab2pt.records[n].items():
			print >>stderr, (k+":").ljust(15), v
		print >>stderr, "--"
	#import time
	#time.sleep(5)
	#print '\n'.join(ab2pt.records[-1].values())
