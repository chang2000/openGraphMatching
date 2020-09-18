# Use this file to generate the networkx instance.

import networkx as nx

def convert_graph(filepath):
    file_obj = open(filepath, "r")
    contents = file_obj.readline()
    print(contents)
    print(type(contents))
    contents = file_obj.readline()
    print(contents)
    print(type(contents))
    contents = file_obj.readline()
    print(contents)
    print(type(contents))

