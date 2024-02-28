import argparse
import json
import asyncio
import logging
import time

logger = logging.getLogger(__name__)


class InvalidDAGError(Exception):
    """Exception raised for invalid DAG.

    Attributes:
        message -- explanation of the error
    """

    pass


def find_start_node(dag):
    """
    Find the start node in a directed acyclic graph (DAG).

    Args:
        dag (dict): The DAG represented as a dictionary, where the keys are nodes and the values are their dependencies.

    Returns:
        str: The start node in the DAG.

    Raises:
        InvalidDAGError: If no start node is found in the DAG.
    """
    for k, v in dag.items():
        if "start" in v:
            return k
    raise InvalidDAGError("No start node in this DAG")


def validate_acyclic(input_graph, start_node):
    """
    Validates that no cycles exist in the input graph.

    Args:
        input_graph (dict): The directed acyclic graph (DAG) represented as a dictionary, where the keys are nodes
                            and the values are dictionaries containing information about the node's edges.
        start_node: The node to start the traversal from.

    Raises:
        InvalidDAGError: If a cycle is detected in the DAG.

    Returns:
        None
    """
    visited = set()

    def visit(node):
        if node in visited:
            raise InvalidDAGError(
                f"Cycle detected in DAG. Node {node} has already been visited"
            )
        visited.add(node)
        for next_node in input_graph[node]["edges"]:
            visit(next_node)
        visited.remove(node)

    visit(start_node)


async def process_edge(dag, node, next_node, wait):
    """
    Process an edge in a directed acyclic graph (DAG).

    Args:
        dag (dict): The DAG represented as a dictionary.
        node (str): The current node.
        next_node (str): The next_node to process.
        wait (int): The wait time in seconds before processing the next node.
        visited (set): A set of visited nodes to detect cycles.

    Raises:
        InvalidDAGError: If a cycle is detected in the DAG.

    Returns:
        None
    """
    logger.debug(
        f"Waiting {wait} seconds before visiting {next_node}, {time.asctime()}"
    )
    await asyncio.sleep(wait)
    logger.debug(f"Visiting {next_node} from {node}, {time.asctime()}")
    logger.info(f"{next_node}")
    edges_to_process = (
        process_edge(dag, next_node, next_next_node, next_wait)
        for next_next_node, next_wait in dag[next_node]["edges"].items()
    )
    await asyncio.gather(*edges_to_process)


async def traverse_dag(input_graph, start_node):
    """
    Traverses a directed acyclic graph starting from the appropriate start node.

    Args:
        dag (dict): The DAG represented as a dictionary.

    Returns:
        None
    """
    logger.debug(f"Starting at {start_node}, {time.asctime()}")
    logger.info(f"{start_node}")
    edges_to_process = (
        process_edge(input_graph, start_node, next_node, wait)
        for next_node, wait in input_graph[start_node]["edges"].items()
    )
    await asyncio.gather(*edges_to_process)
    logger.info("Done!")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dag", help="The directed acyclic graph in JSON format")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level, default is INFO",
    )
    args = parser.parse_args()
    logging.basicConfig(format="%(message)s", level=args.log_level)

    try:
        dag = json.loads(args.dag)
    except json.JSONDecodeError:
        logger.error("Invalid JSON")
        exit(1)
    try:
        start_node = find_start_node(dag)
        validate_acyclic(dag, start_node)
        await asyncio.gather(traverse_dag(dag, start_node))
    except InvalidDAGError as e:
        logging.error(e)
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
