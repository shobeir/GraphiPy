
[![Downloads](https://pepy.tech/badge/graphipy)](https://pepy.tech/project/graphipy) [![Downloads](https://pepy.tech/badge/graphipy/month)](https://pepy.tech/project/graphipy) [![Downloads](https://pepy.tech/badge/graphipy/week)](https://pepy.tech/project/graphipy)

# GraphiPy

A Universal Social Data Extractor

<img src="https://yt3.ggpht.com/-E1RbjCNoU_4/AAAAAAAAAAI/AAAAAAAAAFA/aL_icowG2fg/s288-mo-c-c0xffffffff-rj-k-no/photo.jpg" width="150">



GraphiPy simplifies the extraction of data from different social media websites. Instead of having to study the different APIs of each website, just provide the API keys and use GraphiPy!

Currently, GraphiPy provides support to 7 different websites:
- [Reddit](https://www.reddit.com/dev/api/)
- [Facebook](https://developers.facebook.com/docs/graph-api/)
- [LinkedIn](https://developer.linkedin.com/docs/rest-api#) (Work in progress) 
- [Pinterest](https://developers.pinterest.com/docs/getting-started/introduction/)
- [Tumblr](https://www.tumblr.com/docs/en/api/v2)
- [Twitter](https://developer.twitter.com/en/docs)
- [YouTube](https://developers.google.com/youtube/v3/)

## Installation
GraphiPy is uploaded on PyPI and can be found [here](https://pypi.org/project/GraphiPy/).

To install GraphiPy, run
```pip install GraphiPy```

Please note that GraphiPy does not support Python 2 and only works on Python 3.

## Video Demonstration
[![GraphiPy Video](https://i.ytimg.com/vi/I_86Q3LQvNQ/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLCsASAnS2ZqfmCS2_mz8b1tP0TLvg)](http://www.youtube.com/watch?v=I_86Q3LQvNQ)

## Data Strcuture
GraphiPy acts like a Graph in which all the different information are stored as nodes and connections between different nodes will be stored as edges.

Currently, we have 3 graph types:
- [Dictionary](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
- [Pandas](https://pandas.pydata.org/)
- [Neo4j](https://neo4j.com/)

All graph types are based on a class called [BaseGraph](https://github.com/shobeir/GraphiPy/blob/master/graphipy/graph/graph_base.py)

- [Dictionary Graph](https://github.com/shobeir/GraphiPy/blob/master/graphipy/graph/graph_dict.py)
To provide easy access, the type of the nodes and edges are stored as keys while the rows of data are stored as values. The rows of data is also a dictionary, with the \_id of the nodes and edges as keys (to avoid duplicate data) and the values would be the node and edge objects.

- [Pandas Graph](https://github.com/shobeir/GraphiPy/blob/master/graphipy/graph/graph_pandas.py)
Similar to the Dictionary Graph, the type of nodes and edges are stored as keys and the dataframes are stored as values.
Since inserting rows one by one into the dataframe takes polynomial time, the implementation uses the help of Python's dictionary. After a certain number of elements are inside the dictionaries, all of them are converted into dataframes and appended into the existing dataframes.

- [Neo4j Graph](https://github.com/shobeir/GraphiPy/blob/master/graphipy/graph/graph_neo4j.py)
GraphiPy directly connects and inserts to your Neo4j database. In order to avoid duplicate data, MERGE is used instead of CREATE. Thus, whenever an existing node \_id is inserted, its attributes are updated instead of inserting a completely new node.

## [API Demos](https://github.com/shobeir/GraphiPy/tree/master/demo)

For more information on how to use GraphiPy, please see one of the notebooks:
- [Reddit](https://github.com/shobeir/GraphiPy/blob/master/demo/RedditDemo.ipynb)
- [Facebook](https://github.com/shobeir/GraphiPy/blob/master/demo/FacebookDemo.ipynb)
- [LinkedIn](https://github.com/shobeir/GraphiPy/blob/master/demo/LinkedinDemo.ipynb)
- [Pinterest](https://github.com/shobeir/GraphiPy/blob/master/demo/PinterestDemo.ipynb)
- [Tumblr](https://github.com/shobeir/GraphiPy/blob/master/demo/TumblrDemo.ipynb)
- [Twitter](https://github.com/shobeir/GraphiPy/blob/master/demo/TwitterDemo.ipynb)
- [YouTube](https://github.com/shobeir/GraphiPy/blob/master/demo/YoutubeDemo.ipynb)

## [Data Exportation and Visualization with NetworkX](https://github.com/shobeir/GraphiPy/blob/master/graphipy/exportnx.py)
GraphiPy can also export data as CSV files and visualize the graphs using NetworkX. It is also possible to convert from one graph type to another (e.g. from Pandas to Neo4j and vice versa). For more information, see [this notebook](https://github.com/shobeir/GraphiPy/blob/master/demo/DataExportDemo.ipynb)

- Gephi Support: 
[Gephi](https://gephi.org/) is an open-source software for network visualization and analysis. It helps data analysts to intuitively reveal patterns and trends, highlight outliers and tells stories with their data.
The csv files exported from Graphify can be directly imported to Gephi.
The below figure shows data visualization (via Gephi) of 20 youtube videos with keyword "dota2" extracted via GraphiPy 
![Data of 20 youtube videos with keyword "dota2"](https://user-images.githubusercontent.com/25040463/48648253-85e33080-e9a3-11e8-9412-cf0f2bd286de.png)

## Folder Structure
```
.
├── demo
|   ├── DataExportDemo.ipynb
|   ├── FacebookDemo.ipynb
|   ├── LinkedinDemo.ipynb
|   ├── PinterestDemo.ipynb
|   ├── RedditDemo.ipynb
|   ├── TumblrDemo.ipynb
|   ├── TwitterDemo.ipynb
|   └── YoutubeDemo.ipynb
├── graphipy
|   ├── api
|   |   ├── _init_.py
|   |   ├── facebook_api.py	
|   |   ├── linkedin_api.py	
|   |   ├── pinterest_api.py
|   |   ├── reddit_api.py	
|   |   ├── tumblr_api.py	
|   |   ├── twitter_api.py	
|   |   └── youtube_api.py	
|   ├── graph
|   |   ├── _init_.py
|   |   ├── graph_base.py
|   |   ├── graph_dict.py
|   |   ├── graph_neo4j.py
|   |   └── graph_pandas.py
|   ├── _init_.py
|   ├── exportnx.py
|   └── graphipy.py
├── .gitignore 
├── README.md
└── requirements.txt
```
| Folder/Filename | Description |
|----|:---:|
| demo | Jupyter notebooks explaining how to use the library in detail |
| graphipy | The major directory of the library containing classes for all social media platforms, graph data structure and exporting functionalities |
| graphipy/api | Class definitions for all social media platforms, including fetch functions and customized nodes and edges  |
| graphipy/graph | Definitions of the graph data structure implemented with dictionary, Pandas and Neo4J  |
| requirements.txt | All dependencies  |

