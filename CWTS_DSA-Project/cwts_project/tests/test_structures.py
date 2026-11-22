"""Run:  python -m unittest discover tests   (from the project folder)"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from structures import RecordDictionary, RecordList, ServiceQueue
from algorithms import binary_search, selection_sort


class TestStructures(unittest.TestCase):
    def test_dictionary(self):
        d = RecordDictionary()
        self.assertTrue(d.add("a", 1))
        self.assertFalse(d.add("a", 2))      # duplicate key
        self.assertFalse(d.add("", 3))       # blank key
        self.assertEqual(d.get("a"), 1)
        self.assertIsNone(d.get("zzz"))
        self.assertTrue(d.update("a", 5))
        self.assertFalse(d.update("zzz", 5))
        self.assertEqual(d.remove("a"), 5)
        self.assertTrue(d.is_empty())

    def test_list(self):
        l = RecordList()
        l.add("x"); l.add("y")
        self.assertEqual(l.get(1), "y")
        self.assertIsNone(l.get(5))
        self.assertIsNone(l.remove("nope"))
        self.assertEqual(l.remove("x"), "x")
        self.assertEqual(l.size(), 1)

    def test_queue_is_fifo(self):
        q = ServiceQueue()
        q.enqueue(1); q.enqueue(2)
        self.assertEqual(q.peek(), 1)
        self.assertEqual(q.dequeue(), 1)
        self.assertEqual(q.dequeue(), 2)
        self.assertIsNone(q.dequeue())


class TestAlgorithms(unittest.TestCase):
    def test_sort_returns_new_list(self):
        data = [3, 1, 2]
        self.assertEqual(selection_sort(data), [1, 2, 3])
        self.assertEqual(selection_sort(data, reverse=True), [3, 2, 1])
        self.assertEqual(data, [3, 1, 2])

    def test_sort_by_key(self):
        rows = [{"n": "b"}, {"n": "a"}]
        self.assertEqual(selection_sort(rows, lambda r: r["n"])[0]["n"], "a")

    def test_binary_search(self):
        arr = [1, 3, 5, 7]
        self.assertEqual(binary_search(arr, 5), 2)
        self.assertEqual(binary_search(arr, 4), -1)
        self.assertEqual(binary_search([], 1), -1)


if __name__ == "__main__":
    unittest.main()
