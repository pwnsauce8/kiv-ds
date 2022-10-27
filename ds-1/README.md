# Assignment #1

Objective of this task is to implement a distributed application for electing 1 node as master (coordinator) from N identical nodes. 
After electing process master node controls the "coloring" of nodes with following rules:

* Master must be always `GREEN`
* 1/3 of nodes will be `GREEN`
* 2/3 of nodes will be `RED`

## General info

This project uses **Bully algorithm** for selecting master node.

### Assumptions

* Each node knows the IP of every other node.
* A process initiates an election if it notices that the coordinator has failed.

### Algorithm Details

* Each node N is traversing through all nodes
* If any of nodes will have larger IP number, the Coordinator found
* Coorinator sends `set-coordinator` message for all nodes 

## Requirements

* **Vagrant**
* **Docker**

## Build and run

### Settings

Change node count is possible in `Vagrantfile` on line number `2`:

```bash
# Number of nodes to start:
NODES_COUNT = 3
```

### Run

To start vagrant In main folder `/ds-1` run command:

```bash
vagrant up
```
