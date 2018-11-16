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

For more information on how to use GraphiPy, please see one of the notebooks:
- [Reddit(https://github.com/shobeir/GraphiPy/blob/master/demo/RedditDemo.ipynb)
- [Facebbok](https://github.com/shobeir/GraphiPy/blob/master/demo/FacebookDemo.ipynb)
- [LinkedIn](https://github.com/shobeir/GraphiPy/blob/master/demo/LinkedinDemo.ipynb)
- [Pinterest](https://github.com/shobeir/GraphiPy/blob/master/demo/PinterestDemo.ipynb)
- [Tumblr](https://github.com/shobeir/GraphiPy/blob/master/demo/TumblrDemo.ipynb)
- [Twitter](https://github.com/shobeir/GraphiPy/blob/master/demo/TwitterDemo.ipynb)
- [YouTube](https://github.com/shobeir/GraphiPy/blob/master/demo/YoutubeDemo.ipynb)

GraphiPy can also export data as CSV files and visualize the graphs using NetworkX. For more information, see [this notebook](https://github.com/shobeir/GraphiPy/blob/master/demo/DataExportDemo.ipynb)
