import re
from mechanize import Browser

br = Browser()

def getLinks():
	#print "Inside Main Function"
	
	#response=br.open("http://www.cs.indiana.edu/~djcran/")
	
	response=br.open("http://www.soic.indiana.edu/computer-science/")
	#print "Link Opened"
	#print response.read()
	
	for link in br.links(url_regex='(.*?indiana)'):
		#print link.text
		print link.url
		loopResp=br.follow_link(link)
		#print loopResp.geturl()
		print "###############################################################"
		br.back()


if __name__ == "__main__":
        print "Calling Main"
        main()
        print "Call to Main ended"
