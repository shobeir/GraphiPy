# GraphiPy
A Universal Social Data Extractor

GraphiPy simplifies the extraction of data from different social media websites. Instead of having to study the different APIs of each website, just provide the API keys and use GraphiPy!

Currently, GraphiPy provides support to 7 different websites:
- [Reddit](https://www.reddit.com/dev/api/)
- [Facebbok](https://developers.facebook.com/docs/graph-api/)
- [LinkedIn](https://developer.linkedin.com/docs/rest-api#) (Work in progress) 
- [Pinterest](https://developers.pinterest.com/docs/getting-started/introduction/)
- [Tumblr](https://www.tumblr.com/docs/en/api/v2)
- [Twitter](https://developer.twitter.com/en/docs)
- [YouTube](https://developers.google.com/youtube/v3/)

## How it Works
GraphiPy acts like a Graph in which all the different information are stored as nodes and connections between different nodes will be stored as edges.

Currently, we have 3 graph types:
- [Dictionary](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
- [Pandas](https://pandas.pydata.org/)
- [Neo4j](https://neo4j.com/)

All graph types are based on a class called [BaseGraph](https://github.com/shobeir/GraphiPy/blob/master/graphipy/graph/graph_base.py)

## [Dictionary Graph](https://github.com/shobeir/GraphiPy/blob/master/graphipy/graph/graph_dict.py)
To provide easy access, the type of the nodes and edges are stored as keys while the rows of data are stored as values. The rows of data is also a dictionary, with the \_id of the nodes and edges as keys (to avoid duplicate data) and the values would be the node and edge objects.

## [Pandas Graph](https://github.com/shobeir/GraphiPy/blob/master/graphipy/graph/graph_pandas.py)
Similar to the Dictionary Graph, the type of nodes and edges are stored as keys and the dataframes are stored as values.

Since inserting rows one by one into the dataframe takes polynomial time, the implementation uses the help of Python's dictionary. After a certain number of elements are inside the dictionaries, all of them are converted into dataframes and appended into the existing dataframes.

## [Neo4j Graph](https://github.com/shobeir/GraphiPy/blob/master/graphipy/graph/graph_neo4j.py)
GraphiPy directly connects and inserts to your Neo4j database. In order to avoid duplicate data, MERGE is used instead of CREATE. Thus, whenever an existing node \_id is inserted, its attributes are updated instead of inserting a completely new node.

For more information on how to use GraphiPy, please see one of the notebooks:
- [Reddit](https://github.com/shobeir/GraphiPy/blob/master/demo/RedditDemo.ipynb)
- [Facebbok](https://github.com/shobeir/GraphiPy/blob/master/demo/FacebookDemo.ipynb)
- [LinkedIn](https://github.com/shobeir/GraphiPy/blob/master/demo/LinkedinDemo.ipynb)
- [Pinterest](https://github.com/shobeir/GraphiPy/blob/master/demo/PinterestDemo.ipynb)
- [Tumblr](https://github.com/shobeir/GraphiPy/blob/master/demo/TumblrDemo.ipynb)
- [Twitter](https://github.com/shobeir/GraphiPy/blob/master/demo/TwitterDemo.ipynb)
- [YouTube](https://github.com/shobeir/GraphiPy/blob/master/demo/YoutubeDemo.ipynb)

## [Data Exportation and Visualization with NetworkX](https://github.com/shobeir/GraphiPy/blob/master/graphipy/exportnx.py)
GraphiPy can also export data as CSV files and visualize the graphs using NetworkX. It is also possible to convert from one graph type to another (e.g. from Pandas to Neo4j and vice versa). For more information, see [this notebook](https://github.com/shobeir/GraphiPy/blob/master/demo/DataExportDemo.ipynb)


