Focused-Web-Crawling
====================

PROBABILISTIC MODELS FOR FOCUSED WEB CRAWLING

Our project can be divided into three significant parts:
  Data Collection 
	Pattern Learning 
	Focused Crawling
 
DATA COLLECTION:
In the original paper the authors have used the Yahoo API in-link service for extracting page sequences, but the in-link service has moved to Bing and doesn’t support in-link service anymore. We plan to use some open source in-link service for data collection.
The data collection will be carried out as follows.
	Web Graph Creation
	A target node will be set up as the root node and the links attached to it will be retrieved using in-links.
	This will form two layers of the graph.
	This process will be continued until all the links are linked to each other. ( four layers in the diagram shown below)
	 In the end the nodes which are similar to the target will be marked as target.
 

	Extraction of Page Sequences & State Sequences
	The node sequence can be extracted as 9 → 7 → 4 → 2→0 and its corresponding state sequence can be T1 → T0 → T1 → T1 → T0.
	These state sequences are further used as training data.
PATTERN LEARNING:
This is the second stage of our project. The main objective of this stage is to input data and estimate parameters for the model. The model we plan to use for the project is either Maximum entropy Markov Model (Directed Graphs) or Conditional Random Fields (Undirected Graphs). 
The MEMM we plan to use can be represented as follows in figure 1:

                 
Figure 1: MEMM model Figure 2: Simplified MEMM converted to HMM
Where St is the hidden state for tth linked to the target page
For example: Let t0 be the target page and t_4  t_(3 ) t_2  t_1   be linked to the target t0 in the given sequence then the title. Keywords, anchor text & URL Tokens of these pages will be the observation Ot for each hidden state St.
Thus the MEMM can be represented as a HMM as shown in figure 2.

FOCUSED CRAWLING:
For focused crawling we plan to follow a simple flowchart as shown below which we have adapted from the paper:
 

