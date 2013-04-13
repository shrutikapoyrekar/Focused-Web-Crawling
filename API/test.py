from lsapi import lsapi
l = lsapi('member-a1c2050723', '9776ad0162ea4c492b2b4d56a0cfcd1a')
print "Calling API"
mozMetrics = l.urlMetrics('http://www.google.com')
#print mozMetrics
#links = l.links('http://www.google.com')

links = l.links('www.soic.indiana.edu/computer-science/')
#print "\n\n", links
for items in links:
	#print items
	for key, value in items.iteritems():
		if (key == "uu"):
			print key, value	
print "Call to API Ended"
