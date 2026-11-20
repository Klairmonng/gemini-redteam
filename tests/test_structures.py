import random
import unittest

from datalab.interfaces import ListADT, MapADT, SortedMapADT
from datalab.structures import BinarySearchTree, DoublyLinkedList, HashMap, fnv1a


def assert_bst(test, tree):
    """The tree's defining rule: an in-order walk gives strictly increasing keys."""
    keys = list(tree.keys())
    test.assertEqual(len(keys), len(tree))
    test.assertTrue(all(a < b for a, b in zip(keys, keys[1:])), "in-order keys are not strictly increasing")


class TestInterfaces(unittest.TestCase):
    """[R-DS-1] Technique: checklist. Every structure implements its interface."""

    def test_TC_IF_01_structures_implement_interfaces(self):
        self.assertIsInstance(DoublyLinkedList(), ListADT)
        self.assertIsInstance(HashMap(), MapADT)
        self.assertIsInstance(BinarySearchTree(), SortedMapADT)

    def test_TC_IF_02_incomplete_structure_is_refused(self):
        class Half(ListADT):
            def add_first(self, element):
                pass
        with self.assertRaises(TypeError):
            Half()


class TestDoublyLinkedListStates(unittest.TestCase):
    """[R-DS-2] Technique: state transition testing.

    States: EMPTY, ONE (one element), MANY (two or more). Each test drives the list
    through a transition and checks the state it ends in, including the transitions
    that must be refused (removing from EMPTY).
    """

    def assert_contents(self, dll, expected):
        self.assertEqual(len(dll), len(expected))
        self.assertEqual(list(dll), expected)
        self.assertEqual(list(reversed(dll)), expected[::-1])
        self.assertEqual(dll.is_empty(), not expected)

    def test_TC_DLL_01_empty_state(self):
        dll = DoublyLinkedList()
        self.assert_contents(dll, [])
        for op in (dll.first, dll.last, dll.remove_first, dll.remove_last):
            with self.assertRaises(IndexError):
                op()

    def test_TC_DLL_02_empty_to_one_and_back_from_the_front(self):
        dll = DoublyLinkedList()
        dll.add_first("a")
        self.assert_contents(dll, ["a"])
        self.assertEqual(dll.first(), dll.last())
        self.assertEqual(dll.remove_first(), "a")
        self.assert_contents(dll, [])

    def test_TC_DLL_03_empty_to_one_and_back_from_the_back(self):
        dll = DoublyLinkedList()
        dll.add_last("a")
        self.assertEqual(dll.remove_last(), "a")
        self.assert_contents(dll, [])
        dll.add_last("b")  # usable again after going back to EMPTY
        self.assert_contents(dll, ["b"])

    def test_TC_DLL_04_one_to_many_keeps_order(self):
        dll = DoublyLinkedList()
        dll.add_last(2)
        dll.add_last(3)
        dll.add_first(1)
        self.assert_contents(dll, [1, 2, 3])
        self.assertEqual((dll.first(), dll.last()), (1, 3))

    def test_TC_DLL_05_many_to_one_to_empty(self):
        dll = DoublyLinkedList([1, 2, 3])
        self.assertEqual(dll.remove_first(), 1)
        self.assertEqual(dll.remove_last(), 3)
        self.assert_contents(dll, [2])
        self.assertEqual(dll.remove_last(), 2)
        self.assert_contents(dll, [])

    def test_TC_DLL_06_remove_if_head_middle_tail(self):
        dll = DoublyLinkedList([0, 1, 2, 3, 4, 5, 6])
        removed = dll.remove_if(lambda x: x in (0, 3, 6))
        self.assertEqual(removed, 3)
        self.assert_contents(dll, [1, 2, 4, 5])

    def test_TC_DLL_07_remove_if_everything_goes_to_empty(self):
        dll = DoublyLinkedList(range(5))
        self.assertEqual(dll.remove_if(lambda x: True), 5)
        self.assert_contents(dll, [])
        dll.add_first(9)
        self.assert_contents(dll, [9])

    def test_TC_DLL_08_to_array(self):
        self.assertEqual(DoublyLinkedList("abc").to_array(), ["a", "b", "c"])
        self.assertEqual(DoublyLinkedList().to_array(), [])


class TestDoublyLinkedListIndex(unittest.TestCase):
    """[R-DS-2] Technique: boundary value analysis on get(index) for a list of 10 elements.
    Valid range 0..9; the values on and next to each edge are tested, plus the middle
    where get switches from walking forwards to walking backwards."""

    def setUp(self):
        self.dll = DoublyLinkedList(range(10))

    def test_TC_DLL_09_valid_edges_and_middle(self):
        for index in (0, 1, 4, 5, 8, 9):
            self.assertEqual(self.dll.get(index), index)

    def test_TC_DLL_10_invalid_edges(self):
        for index in (-1, 10):
            with self.assertRaises(IndexError):
                self.dll.get(index)

    def test_TC_DLL_11_empty_list_has_no_valid_index(self):
        with self.assertRaises(IndexError):
            DoublyLinkedList().get(0)


class TestHashMapBehaviour(unittest.TestCase):
    """[R-DS-3] Technique: equivalence partitioning.

    Key classes: str, int, tuple, and keys that look alike across types (1 and "1").
    Operation classes: new key, existing key, missing key.
    """

    def test_TC_HM_01_put_get_for_each_key_type(self):
        m = HashMap()
        for key, value in (("text", 1), (42, 2), (("judge", 1), 3), ("", 4), (-7, 5)):
            self.assertIsNone(m.put(key, value))
            self.assertEqual(m.get(key), value)
            self.assertIn(key, m)
        self.assertEqual(len(m), 5)

    def test_TC_HM_02_lookalike_keys_of_different_types_stay_apart(self):
        m = HashMap()
        m.put(1, "int")
        m.put("1", "str")
        self.assertEqual((m.get(1), m.get("1"), len(m)), ("int", "str", 2))
        self.assertNotEqual(fnv1a(1), fnv1a("1"))

    def test_TC_HM_03_existing_key_is_replaced_not_added(self):
        m = HashMap()
        m.put("k", 1)
        self.assertEqual(m.put("k", 2), 1)
        self.assertEqual((m.get("k"), len(m)), (2, 1))

    def test_TC_HM_04_missing_key(self):
        m = HashMap()
        m.put("a", 1)
        self.assertIsNone(m.get("b"))
        self.assertEqual(m.get("b", "default"), "default")
        self.assertNotIn("b", m)
        self.assertIsNone(m.remove("b"))
        self.assertEqual(len(m), 1)

    def test_TC_HM_05_remove_existing_key(self):
        m = HashMap()
        m.put("a", 1)
        m.put("b", 2)
        self.assertEqual(m.remove("a"), 1)
        self.assertNotIn("a", m)
        self.assertEqual((len(m), m.get("b")), (1, 2))

    def test_TC_HM_06_hash_is_deterministic(self):
        self.assertEqual(fnv1a("gemini|direct|L4|r1"), fnv1a("gemini|direct|L4|r1"))

    def test_TC_HM_07_bad_capacity_is_refused(self):
        for capacity in (0, 3, 12):
            with self.assertRaises(ValueError):
                HashMap(capacity)


class TestHashMapCollisions(unittest.TestCase):
    """[R-DS-3] Technique: error guessing on the worst case. A hash function that sends every key
    to the same bucket makes one long chain; the map must still be correct, including
    removal from the head, middle and end of that chain."""

    def setUp(self):
        self.m = HashMap(hash_function=lambda key: 0)
        for i in range(10):
            self.m.put(i, str(i))

    def test_TC_HM_08_all_keys_found_in_one_chain(self):
        self.assertEqual(self.m.stats()["longest_chain"], 10)
        for i in range(10):
            self.assertEqual(self.m.get(i), str(i))

    def test_TC_HM_09_remove_from_chain_head_middle_end(self):
        # New entries go to the front of a chain, so 9 is the head and 0 the end.
        for key in (9, 5, 0):
            self.assertEqual(self.m.remove(key), str(key))
            self.assertNotIn(key, self.m)
        self.assertEqual(sorted(self.m.keys()), [1, 2, 3, 4, 6, 7, 8])


class TestHashMapResize(unittest.TestCase):
    """[R-DS-3] Technique: boundary value analysis on the load factor. With 16 buckets and a
    maximum load of 0.75 the map holds 12 entries; the 13th must double it to 32."""

    def test_TC_HM_10_twelve_entries_fit(self):
        m = HashMap(16)
        for i in range(12):
            m.put(i, i)
        self.assertEqual((m.capacity, m.resizes), (16, 0))

    def test_TC_HM_11_thirteenth_entry_doubles_capacity(self):
        m = HashMap(16)
        for i in range(13):
            m.put(i, i)
        self.assertEqual((m.capacity, m.resizes), (32, 1))
        for i in range(13):
            self.assertEqual(m.get(i), i)

    def test_TC_HM_12_replacing_at_the_limit_does_not_resize(self):
        m = HashMap(16)
        for i in range(12):
            m.put(i, i)
        m.put(11, "again")
        self.assertEqual((m.capacity, len(m)), (16, 12))

    def test_TC_HM_13_many_resizes_against_a_dict(self):
        rng = random.Random(1)
        m, reference = HashMap(), {}
        for _ in range(20000):
            key = rng.randrange(5000)
            if rng.random() < 0.3:
                self.assertEqual(m.remove(key), reference.pop(key, None))
            else:
                value = rng.random()
                self.assertEqual(m.put(key, value), reference.get(key))
                reference[key] = value
        self.assertEqual(len(m), len(reference))
        self.assertEqual(dict(m.items()), reference)
        self.assertLessEqual(m.stats()["load_factor"], HashMap.MAX_LOAD)


class TestTreeRemove(unittest.TestCase):
    """[R-DS-4] Technique: decision table for BinarySearchTree.remove.

    | Rule | Left child | Right child | Node is root | Expected action |
    |---|---|---|---|---|
    | R1 | no | no | yes | tree becomes empty |
    | R2 | no | no | no | parent's link set to None |
    | R3 | yes | no | yes | left child becomes root |
    | R4 | yes | no | no | parent links to left child |
    | R5 | no | yes | yes | right child becomes root |
    | R6 | no | yes | no | parent links to right child |
    | R7 | yes | yes | yes | root takes in-order successor |
    | R8 | yes | yes | no, successor is the right child | node takes successor |
    | R9 | yes | yes | no, successor deeper on the left | node takes successor |
    """

    def build(self, keys):
        tree = BinarySearchTree()
        for k in keys:
            tree.put(k, f"v{k}")
        return tree

    def check_remove(self, keys, key):
        tree = self.build(keys)
        self.assertEqual(tree.remove(key), f"v{key}")
        self.assertNotIn(key, tree)
        assert_bst(self, tree)
        self.assertEqual(list(tree.keys()), sorted(k for k in keys if k != key))
        for k in keys:
            if k != key:
                self.assertEqual(tree.get(k), f"v{k}")
        return tree

    def test_TC_BST_01_R1_leaf_root(self):
        tree = self.check_remove([5], 5)
        self.assertEqual((len(tree), tree.height()), (0, 0))

    def test_TC_BST_02_R2_leaf(self):
        self.check_remove([5, 3, 8], 3)

    def test_TC_BST_03_R3_root_with_left_only(self):
        tree = self.check_remove([5, 3, 1], 5)
        self.assertEqual(tree.min_key(), 1)

    def test_TC_BST_04_R4_inner_with_left_only(self):
        self.check_remove([5, 3, 1, 8], 3)

    def test_TC_BST_05_R5_root_with_right_only(self):
        self.check_remove([5, 8, 9], 5)

    def test_TC_BST_06_R6_inner_with_right_only(self):
        self.check_remove([5, 3, 4, 8], 3)

    def test_TC_BST_07_R7_root_with_two_children(self):
        self.check_remove([5, 3, 8, 7, 9], 5)

    def test_TC_BST_08_R8_successor_is_right_child(self):
        self.check_remove([10, 5, 3, 7, 15], 5)

    def test_TC_BST_09_R9_successor_deeper(self):
        self.check_remove([10, 5, 3, 8, 7, 6, 15], 5)

    def test_TC_BST_10_missing_key(self):
        tree = self.build([5, 3, 8])
        self.assertIsNone(tree.remove(4))
        self.assertIsNone(BinarySearchTree().remove(1))
        self.assertEqual(len(tree), 3)


class TestTreeBehaviour(unittest.TestCase):
    """[R-DS-4] Technique: equivalence partitioning (empty tree, one key, many keys, existing and
    missing keys) plus a model-based check against a dict."""

    def test_TC_BST_11_empty_tree(self):
        tree = BinarySearchTree()
        self.assertEqual((len(tree), tree.height(), list(tree.items())), (0, 0, []))
        for op in (tree.min_key, tree.max_key):
            with self.assertRaises(KeyError):
                op()

    def test_TC_BST_12_put_replaces_equal_key(self):
        tree = BinarySearchTree()
        self.assertIsNone(tree.put("a", 1))
        self.assertEqual(tree.put("a", 2), 1)
        self.assertEqual((tree.get("a"), len(tree)), (2, 1))

    def test_TC_BST_13_min_max_and_sorted_walk(self):
        keys = [50, 20, 70, 10, 30, 60, 80]
        tree = BinarySearchTree()
        for k in keys:
            tree.put(k, None)
        self.assertEqual((tree.min_key(), tree.max_key()), (10, 80))
        self.assertEqual(list(tree.keys()), sorted(keys))
        self.assertEqual(tree.height(), 3)

    def test_TC_BST_14_tuple_keys_like_the_dataset(self):
        tree = BinarySearchTree()
        for key in [(300, "b"), (300, "a"), (12, "z"), (2208, "x")]:
            tree.put(key, key)
        self.assertEqual(list(tree.keys()), [(12, "z"), (300, "a"), (300, "b"), (2208, "x")])

    def test_TC_BST_15_random_operations_against_a_dict(self):
        rng = random.Random(2)
        tree, reference = BinarySearchTree(), {}
        for _ in range(5000):
            key = rng.randrange(1000)
            if rng.random() < 0.35:
                self.assertEqual(tree.remove(key), reference.pop(key, None))
            else:
                self.assertEqual(tree.put(key, key * 2), reference.get(key))
                reference[key] = key * 2
        assert_bst(self, tree)
        self.assertEqual(list(tree.items()), sorted(reference.items()))


class TestTreeRange(unittest.TestCase):
    """[R-DS-4] Technique: boundary value analysis on range(low, high), which includes low and
    excludes high. Keys are 10, 20, ..., 100."""

    def setUp(self):
        self.tree = BinarySearchTree()
        for k in random.Random(3).sample(range(10, 101, 10), 10):
            self.tree.put(k, k)

    def keys(self, low, high):
        return [k for k, _ in self.tree.range(low, high)]

    def test_TC_BST_16_low_is_included_high_is_excluded(self):
        self.assertEqual(self.keys(30, 60), [30, 40, 50])

    def test_TC_BST_17_values_next_to_the_edges(self):
        self.assertEqual(self.keys(29, 61), [30, 40, 50, 60])
        self.assertEqual(self.keys(31, 59), [40, 50])

    def test_TC_BST_18_whole_tree_and_empty_ranges(self):
        self.assertEqual(self.keys(0, 1000), list(range(10, 101, 10)))
        self.assertEqual(self.keys(41, 49), [])
        self.assertEqual(self.keys(50, 50), [])
        self.assertEqual(self.keys(200, 300), [])
        self.assertEqual(self.keys(-10, 10), [])


class TestTreeShape(unittest.TestCase):
    """[R-DS-4] Technique: error guessing. Sorted input is the known worst case of a tree that
    does not rebalance; random input should stay close to log2(n)."""

    def test_TC_BST_19_sorted_input_makes_a_chain(self):
        tree = BinarySearchTree()
        for k in range(500):
            tree.put(k, k)
        self.assertEqual(tree.height(), 500)
        self.assertEqual(tree.get(499), 499)  # still correct, only slow

    def test_TC_BST_20_random_input_stays_low(self):
        keys = list(range(20000))
        random.Random(4).shuffle(keys)
        tree = BinarySearchTree()
        for k in keys:
            tree.put(k, k)
        self.assertLess(tree.height(), 3 * 15)  # log2(20000) is about 14.3


if __name__ == "__main__":
    unittest.main()
