import itertools
import unittest
from dagplan import plan


class PlannerTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(plan({})['duration'], 0)

    def test_diamond(self):
        result = plan({'a': {'duration': 2}, 'b': {'needs': ['a'], 'duration': 5}, 'c': {'needs': ['a'], 'duration': 1}, 'd': {'needs': ['b', 'c'], 'duration': 3}})
        self.assertEqual(result['duration'], 10)
        self.assertEqual(result['critical_path'], ['a', 'b', 'd'])
        self.assertEqual(result['levels'], [['a'], ['b', 'c'], ['d']])

    def test_duplicate(self):
        self.assertEqual(plan({'a': {}, 'b': {'needs': ['a', 'a']}})['duration'], 2)

    def test_zero(self):
        self.assertEqual(plan({'a': {'duration': 0}, 'b': {'needs': ['a']}})['duration'], 1)

    def test_disconnected(self):
        self.assertEqual(plan({'a': {'duration': 3}, 'b': {'duration': 7}})['critical_path'], ['b'])

    def test_missing(self):
        with self.assertRaises(ValueError):
            plan({'a': {'needs': ['missing']}})

    def test_self_cycle(self):
        with self.assertRaises(ValueError):
            plan({'a': {'needs': ['a']}})

    def test_cycle(self):
        with self.assertRaises(ValueError):
            plan({'a': {'needs': ['b']}, 'b': {'needs': ['a']}})

    def test_bad_durations(self):
        for value in [-1, True, float('nan'), float('inf'), '1']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                plan({'a': {'duration': value}})

    def test_bad_dependencies(self):
        for value in ['abc', [1], None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                plan({'a': {'needs': value}})

    def test_deterministic(self):
        tasks = {'c': {}, 'a': {}, 'b': {'needs': ['a']}}
        expected = plan(tasks)
        for keys in itertools.permutations(tasks):
            self.assertEqual(plan({k: tasks[k] for k in keys}), expected)

    def test_exhaustive_four_node_dags(self):
        nodes = ['a', 'b', 'c', 'd']
        edges = list(itertools.combinations(nodes, 2))
        for mask in range(1 << len(edges)):
            tasks = {n: {'duration': i + 1, 'needs': []} for i, n in enumerate(nodes)}
            for bit, (a, b) in enumerate(edges):
                if mask & (1 << bit):
                    tasks[b]['needs'].append(a)
            result = plan(tasks)
            # Enumerate every dependency path independently as an oracle.
            def paths(n):
                return [[n]] + [p + [n] for d in tasks[n]['needs'] for p in paths(d)]
            oracle = max(sum(tasks[n]['duration'] for n in p) for n in nodes for p in paths(n))
            self.assertEqual(result['duration'], oracle)
            positions = {n: i for i, n in enumerate(result['order'])}
            for n in nodes:
                for dep in tasks[n]['needs']:
                    self.assertLess(positions[dep], positions[n])
                    self.assertLessEqual(result['times'][dep]['finish'], result['times'][n]['start'])


if __name__ == '__main__':
    unittest.main()
