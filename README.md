# Python DAG Traveler

This project is a Python script that traverses a Directed Acyclic Graph (DAG) represented in JSON with a designated start vertex.
The runner follows the edges of the graph and prints the letter of each vertex that it visits. Before it prints that it visited a vertex, it will wait N seconds, where N is the number assigned to the edge.

To help with debugging, enabling debug logging includes some extra prints with timestamps that were not specified in the task description.


### Design choices
I chose to use Python here because it's the language I'm most familiar with. However, I will acknowledge that Python might not be the absolute "best" choice of language for parallel processing because of the global interpreter lock (GIL).

For this task, we want to sleep before visiting each edge. There isn't any processing happening besides waiting for the sleep to end, so we can consider task to be this more I/O bound than CPU bound.

When considering which python library to use to enable concurrency, I weighed three options: 
1. `multiprocessing`
2. `threading`
3. `asyncio`

`multiprocessing` is the only library that truely enables parallelism, however, using it would bound processing by the number of cores that the runner had available. This task doesn't require a lot of CPU, so this seemed like a bad choice.

`threading` enables concurrency, but not true parallelism. Each task would receive a thread that share the same GIL, which switches between them very quickly. Given that this task involves mostly waiting for I/O (sleep), this would have been a fine choice.

`asyncio` also enables concurrency but not true parallelism. Each task receives a coroutine that can be paused and resumed. The coroutines yield control back to the asyncio event loop when waiting for I/O. Tasks only involve printing and waiting, so this seemed like a good choice.

### Prerequisites

You need to have Python 3.7 or higher.

### Installing
Clone the repository 
`git clone https://github.com/duface/dag_traveler.git`

### Usage
```usage: dag_traveler.py [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] dag

positional arguments:
  dag                   The directed acyclic graph in JSON format

optional arguments:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level
```

The script takes a single argument, which is a JSON string representing the DAG to be traversed. Each node in the DAG is represented as a key in the JSON object. The value associated with each key is another JSON object that contains info about the node's edges, and whether this node is the start node. Each edge will be assigned a number, and the running will wait for that many seconds before visiting the vertex at the end of the edge.

Example:
```
python dag_traveler/dag_traveler.py '{"A":{"start":true,"edges":{"B":1,"C":2}},"B":{"edges":{"D":3,"E":4}},"C":{"edges":{"F":5,"G":6}},"D":{"edges":{"H":7}},"E":{"edges":{"H":8}},"F":{"edges":{"H":9}},"G":{"edges":{"H":10}},"H":{"edges":{}}}'
```
```
{
    "A": {"start": true, "edges": {"B": 1, "C": 2}},
    "B": {"edges": {"D": 3, "E": 4}},
    "C": {"edges": {"F": 5, "G": 6}},
    "D": {"edges": {"H": 7}},
    "E": {"edges": {"H": 8}},
    "F": {"edges": {"H": 9}},
    "G": {"edges": {"H": 10}},
    "H": {"edges": {}}
}
```
```mermaid
graph TD
    A((A))
    B((B))
    C((C))
    D((D))
    E((E))
    F((F))
    G((G))
    H((H))
    A -->|1| B
    A -->|2| C
    B -->|3| D
    B -->|4| E
    C -->|5| F
    C -->|6| G
    D -->|7| H
    E -->|8| H
    F -->|9| H
    G -->|10| H
```

output: 
```
A
B
C
D
E
F
G
H
H
H
H
Done!
```
## Running the tests
`python -m unittest tests/test_dag_traveler.py`
