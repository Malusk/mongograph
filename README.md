
# MongoDB Graph Traversal

A demo to showcase the capabilities of MongoDB as a graph database with visualization using d3.js

To get started create a venv and run mongograph.py, this will run a flask server for the HTML. 

The structure of the MongoDB database consists of a nodes and a relationships collection, the included file is a neo4j cypher text from which we are parsing and putting it into MongoDB using cypherParse.py
