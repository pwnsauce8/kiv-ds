# Assignment #3

The aim of this task is to implement a distributed cache application with a binary tree structure. The tree should have depth 3 or 4 levels and must be configurable in Vagrant file. Also, the hierarchical cache structure will be presented as a corresponding model in Apache Zookeeper.

## Conditions

* It will be possible to define which node will be the **root of the tree** and **how many levels** of the tree to be created in the Vagrantfile file.
* The number of levels of the binary tree is configurable and can be either 3 or 4
* All created nodes will connect to the root of the binary tree after the system starts. Current state will be presented in the corresponding Zookeeper model.

## Cache functions

* REST API should be implemented using Open API.
* **GET** - if the given node (the leaf or its parent node) do not holds the value of the key, it will ask a parent node for it. In this way, the query can recursively reach the root node to find the value of the given key. 
* **PUT** - creating a new key-value record on the leaf and also propagate this record to the root node.
* **DELETE** - remove given key-value record from the leaf local cache and up to the root.

## Requirements

* **Vagrant**
* **Docker**

## Build and run

### Settings

Change node count is possible in `Vagrantfile` from line number `9`:

```bash
TREE_LEVEL =  ..
CLIENTS_COUNT = ..
PORT = ..
```

### Run

To start vagrant use following command in main folder `/ds-3`

```bash
vagrant up
```

### Interaction

* User may use [node_ip:5000/docs](node_ip:5000/docs) address for using all GET, PUT, DELETE operations using OpenAPI specification.
* [node_ip:5000/docs](node_ip:5000/get-details) can be using for getting more information about current node

## Cache coherence

In this implementation only root node has consistent data. The leaf’s may have old data stored, because update propagation on PUT and DELETE operations is going up towards the root node and not to the leaf’s.

The first consideration of solving cache coherence problem is updating root and all leaf’s after each PUT and DELETE operations. This solution is good if we need to have newest data on all leaf’s all the time. But it will decrease the speed of the system, due to big amount of leaf’s.

The second consideration is to set timer on a root node to update key-value tables to all nodes each X seconds/minutes/hours/days.. Described solution is suitable for systems, which are not needed a newest data all the time.
