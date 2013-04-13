from bs4 import BeautifulSoup
import re 
import time
import sys
from lsapi import lsapi
from sets import Set
import urllib,urllib2
import json
import pickle
''' 
Global Variables
'''

#Since below is alias for www.soic.indiana.edu/computer-science/
visitedPages=Set(["www.cs.indiana.edu/"])

class page:
	def __init__(self):
		self.url = None
		self.backLinks = None
		self.text = None
		self.score = None
		self.addnlTgtPage=None
		self.atLevel=None
		
	def __init__(self,pUrl=None,pBackLinks=None,pText=None,pScore=None,paddnlTgtPage=False,plevel=None):
		self.url = pUrl
		self.backLinks = pBackLinks
		self.text = pText
		self.score = pScore
		self.addnlTgtPage = paddnlTgtPage
		self.atLevel=plevel
		
def findPathToTarget(graph, startUrl,endUrl, path=[]):
	print "\nInside the findPathToTarget"
	print "startUrl",startUrl
	print "endUrl",endUrl
	path = path + [startUrl]
	if startUrl == endUrl:
		print "Match Found"
		return [path]
	if not graph.has_key(startUrl):
		print "Not in Backiink"
		return []
	paths = []
	for node in graph[''.join(startUrl)]:
		if node.url not in path:
			print node.url
			newpaths = findPathToTarget(graph, node.url, endUrl, path)
			for newpath in newpaths:
				paths.append(newpath)
	return paths


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', element.encode('utf-8'),re.DOTALL):
        return False
    return True

def cosineSimilar(urlOtherText, urlTargetText):
	API_URL="http://www.scurtu.it/apis/documentSimilarity"
	inputDict={}
	inputDict['doc1']=urlTargetText
	inputDict['doc2']=urlOtherText
	params = urllib.urlencode(inputDict)    
	f = urllib2.urlopen(API_URL, params)
	response= f.read()
	responseObject=json.loads(response)  
	#print responseObject
	for key, value in   responseObject.iteritems():
		if key == "result":
		 return value
		 
def extractText(Url):
	urlMod="http://" + Url
	content = urllib2.urlopen(urlMod).read()
	soup = BeautifulSoup(content)
	texts = soup.findAll(text=True)
	visible_texts = filter(visible, texts)
	visible_texts = Set(visible_texts)
	visible_texts = list(visible_texts)
	return visible_texts

def isTarget(score):
	if score>0.8:
		return True 
	else:
		return False

def getBackLinks(Url):
	#print Url
	bLinks=Set([])
	l = lsapi('member-a1c2050723', '9776ad0162ea4c492b2b4d56a0cfcd1a')
	linksList = l.links(Url)
	#print "\n\n", linksList
	for items in linksList:
		#print items
		for key, value in items.iteritems():
			if (key == "uu"):
				#print value	
				bLinks.add(value)
	#picking only 10 backlinks
	bLinks=list(bLinks)
	#print bLinks[0:2]
	
	for link in visitedPages:
		if link in bLinks:
			bLinks.remove(link)
			
	#print bLinks[0:2]
	# Because of the free API limitation.			
	time.sleep( 10 ) 
	return bLinks[0:2]

def printGraph(graph):
	print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	for url, nodes in graph.iteritems():
		print url, nodes
	print "\n"

def createLocalWebGraph(targetPage,visitedPages,graphNodes):
	print "For target Page:", targetPage
	j=0
	graph={}
	visitedPages.add(targetPage)
	bLinks=getBackLinks(targetPage)
	targetpageText=extractText(targetPage)
	score=cosineSimilar(targetpageText, targetpageText)
	print "Back Links of ",targetPage
	print bLinks
	graphNodes.append(page(targetPage,bLinks, targetpageText,score,isTarget(score),0))
	#print graphNodes[j].url
	#print graphNodes[j].backLinks
	#print graphNodes[j].text
	#print graphNodes[j].score
	#print graphNodes[j].addnlTgtPage
	j+=1
	backNodes=[]
	print "\nAfter root node is created"
	printGraph(graph)
	''' 
	Layer 1 of the Local Web Graph
	'''
	print "########################################################################"
	print "Computing for Layer 1"
	print "########################################################################"
	print "\nComputing for node ", targetPage, " (root) backlinks"
	print "------------------------------------------------------------------------------"
	#Using index because of the u prefix bug	
	for i in range(len(bLinks)):
		#print bLinks[i]
		#print type(bLinks[i])
		visitedPages.add(bLinks[i])
		bblinks=getBackLinks(bLinks[i])
		pageText=extractText(bLinks[i])
		score=cosineSimilar(pageText, targetpageText)
		print "\nBack Links of",bLinks[i]
		print bblinks
		graphNodes.append(page(bLinks[i],bblinks,pageText,score,isTarget(score),1))
		backNodes.append(graphNodes[j])
		i+=1
		j+=1
	#print backNodes
	rootBack=j-1
	graph = {graphNodes[0].url:backNodes}
	print "Number of Back links for root:",rootBack
	
	print "\nAfter root node backlinks are converted into node"
	printGraph(graph)
	
	''' 
	Layer 2 of the Local Web Graph
	'''
	print "\n\n########################################################################"
	print "Computing for Layer 2"
	print "########################################################################"
	backNodes1={}
	#Otherwise u get RuntimeError: dictionary changed size during iteration
	graphToLoop1=graph.copy()
	for nodelist in graphToLoop1.itervalues():
		for node in nodelist:
			startJ=j
			print "\nComputing for node ",node.url," backlinks"
			print "------------------------------------------------------------------------------"
			#print node.backLinks
			bLinkTemp=[]
			for i in range(len(node.backLinks)):
				NodeName=node.backLinks[i]
				visitedPages.add(node.backLinks[i])
				bblinks=getBackLinks(node.backLinks[i])
				pageText=extractText(node.backLinks[i])
				score=cosineSimilar(pageText, targetpageText)
				print "\nBack Links of",node.backLinks[i]
				print bblinks
				graphNodes.append(page(node.backLinks[i],bblinks,pageText,score,isTarget(score),2))
				bLinkTemp.append(graphNodes[j])
				i+=1
				j+=1
			
			# Cannot use node.backLinks[i] as it will throw out of range error, we are incrementing i before that
			graph[node.url]=bLinkTemp
			#backNodes1[NodeName]=bLinkTemp
			print "\nNumber of Back links for",node.url, j-startJ
	
	print "\nAfter layer 1 backlinks are converted into node"
	printGraph(graph)
	
	''' 
	Layer 3 of the Local Web Graph
	'''
	print "\n\n########################################################################"
	print "Computing for Layer 3"
	print "########################################################################"
	
	backNodes1={}
	#Otherwise u get RuntimeError: dictionary changed size during iteration
	graphToLoop2=graph.copy()
	for url,nodelist in graphToLoop2.iteritems():
			if url not in graphToLoop1:
				for node in nodelist:	
					startJ=j
					#print startJ
					#print node
					print "\nComputing for node ",node.url," backlinks"
					print "------------------------------------------------------------------------------"
					#print node.backLinks
					bLinkTemp=[]
					for i in range(len(node.backLinks)):
						NodeName=node.backLinks[i]
						visitedPages.add(node.backLinks[i])
						bblinks=getBackLinks(node.backLinks[i])
						pageText=extractText(node.backLinks[i])
						score=cosineSimilar(pageText, targetpageText)
						print "\nBack Links of",node.backLinks[i]
						print bblinks
						graphNodes.append(page(node.backLinks[i], bblinks, pageText,score,isTarget(score),3))
						bLinkTemp.append(graphNodes[j])
						i+=1
						j+=1
					
					# Cannot use node.backLinks[i] as it will throw out of range error, we are incrementing i before that
					graph[node.url]=bLinkTemp
					#backNodes1[NodeName]=bLinkTemp
					print "\nNumber of Back links for",node.url, j-startJ
	

	''' 
	Layer 4 of the Local Web Graph
	'''
	print "\n\n########################################################################"
	print "Computing for Layer 4"
	print "########################################################################"
	
	backNodes1={}
	#Otherwise u get RuntimeError: dictionary changed size during iteration
	graphToLoop3=graph.copy()
	for url,nodelist in graphToLoop3.iteritems():
			if url not in graphToLoop2:
				for node in nodelist:	
					startJ=j
					#print startJ
					#print node
					print "\nComputing for node ",node.url," backlinks"
					print "------------------------------------------------------------------------------"
					#print node.backLinks
					bLinkTemp=[]
					for i in range(len(node.backLinks)):
						NodeName=node.backLinks[i]
						visitedPages.add(node.backLinks[i])
						bblinks=getBackLinks(node.backLinks[i])
						pageText=extractText(node.backLinks[i])
						score=cosineSimilar(pageText, targetpageText)
						print "\nBack Links of",node.backLinks[i]
						print bblinks
						graphNodes.append(page(node.backLinks[i],bblinks,pageText,score,isTarget(score),4))
						bLinkTemp.append(graphNodes[j])
						i+=1
						j+=1
					
					# Cannot use node.backLinks[i] as it will throw out of range error, we are incrementing i before that
					graph[node.url]=bLinkTemp
					#backNodes1[NodeName]=bLinkTemp
					print "\nNumber of Back links for",node.url, j-startJ
	return graph
	
if __name__ == "__main__":
	targetPage=''.join(sys.argv[1:])
	tgtPageList=["www.soic.indiana.edu/computer-science/",]
	graphNodes={}
	graph={}
	path={}
	fileNameList=[]
	for tgtPage in tgtPageList:	
		graphNodes[tgtPage]=[]
		graph[tgtPage]=createLocalWebGraph(tgtPage,visitedPages,graphNodes[tgtPage])
		
		print "\nNode(s) at level 4"
		for node in graphNodes[tgtPage]:
			print node
			if node.atLevel==4:
				print node.url
				
		allPossiblePath={}
		for node in graphNodes[tgtPage]:
			if node.atLevel==4:
				allPossiblePath[node.url]=findPathToTarget(graph[tgtPage],tgtPage,node.url)		
		path[tgtPage]=allPossiblePath
		rx = re.compile('([.%/])')
		fileName="File_" + rx.sub('_',tgtPage)
		fileNameList.append(fileName)
		f = open(fileName, "w")
		#Otherwise you will get RuntimeError: maximum recursion depth exceeded
		sys.setrecursionlimit(50000)
		pickle.dump(graph[tgtPage],f)
		pickle.dump(graphNodes[tgtPage],f)
		pickle.dump(path[tgtPage],f)
		f.close()	
		'''for tgtPage, paths in path.iteritems():
			for key, value in paths.iteritems():		
				print key, value
		'''		
	
	for file in fileNameList:
		f = open(file, "r")
		fgraph = pickle.load(f)
		fgraphNodes = pickle.load(f)
		fpath = pickle.load(f)
		f.close()
	'''
	print "Printing Local Web Graph Object"
	for key, value in fgraph.iteritems():
		print key,"\t", value	
		
	print "Printing Graph Node Object"
	for nodes in fgraphNodes:
		print nodes.url
		
	print "Printing All Possible Path"
	for key,value in fpath.iteritems():
		print key,"\t",value	
	
	print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	
	for node in graphNodes:
		if node.url=="www.indiana.edu/%7Efoodsci/about.shtml":
			print node.url
			print node.backLinks
			print node.text
			print node.score
			print node.addnlTgtPage
	'''