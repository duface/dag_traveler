import asyncio
import unittest
from unittest.mock import call, patch
from dag_traveler.dag_traveler import (
    find_start_node,
    traverse_dag,
    validate_acyclic,
    InvalidDAGError,
)


class TestMain(unittest.TestCase):
    def setUp(self):
        self.dag = {
            "A": {"start": True, "edges": {"B": 1, "C": 2}},
            "B": {"edges": {"D": 3, "E": 4}},
            "C": {"edges": {}},
            "D": {"edges": {}},
            "E": {"edges": {"F": 5, "G": 6}},
            "F": {"edges": {"G": 7}},
            "G": {"edges": {}},
        }

    def test_find_start_node(self):
        start_node = find_start_node(self.dag)
        self.assertEqual(start_node, "A")

    def test_find_start_node_no_start(self):
        with self.assertRaises(InvalidDAGError):
            find_start_node({"A": {"edges": {"B": 5, "C": 7}}})

    def test_validate_acyclic(self):
        start_node = find_start_node(self.dag)
        try:
            validate_acyclic(self.dag, start_node)
        except InvalidDAGError:
            self.fail("validate_dag raised InvalidDAGError unexpectedly!")

    def test_validate_dag_cycle(self):
        cycle_dag = {"A": {"start": True, "edges": {"B": 5}}, "B": {"edges": {"A": 3}}}
        start_node = find_start_node(cycle_dag)
        with self.assertRaises(InvalidDAGError) as context:
            validate_acyclic(cycle_dag, start_node)
        self.assertEqual(
            str(context.exception),
            "Cycle detected in DAG. Node A has already been visited",
        )

    @patch("dag_traveler.dag_traveler.logger.info")
    @patch("asyncio.sleep")
    def test_traverse_dag(self, mock_sleep, mock_logging_info):
        asyncio.run(traverse_dag(self.dag, "A"))
        log_calls = [
            call("A"),
            call("B"),
            call("C"),
            call("D"),
            call("E"),
            call("F"),
            call("G"),
            call("G"),
            call("Done!"),
        ]
        sleep_calls = [call(1), call(2), call(3), call(4), call(5), call(6), call(7)]
        mock_logging_info.assert_has_calls(log_calls, any_order=False)
        mock_sleep.assert_has_calls(sleep_calls, any_order=False)


if __name__ == "__main__":
    unittest.main()
