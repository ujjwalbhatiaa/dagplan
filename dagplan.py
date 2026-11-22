"""Plan a weighted directed acyclic task graph. Python 3.10+, no dependencies."""
import argparse
import heapq
import json
import math


def plan(tasks):
    """Return earliest times and one critical path with unlimited workers.

    Input: {name: {duration: nonnegative number, needs: [names]}}.
    Duration defaults to 1. Duplicate dependencies count once.
    """
    durations, needs = {}, {}
    for name, task in tasks.items():
        if not isinstance(name, str) or not isinstance(task, dict):
            raise ValueError('Tasks must map string names to objects')
        duration = task.get('duration', 1)
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0:
            raise ValueError(f'Invalid duration for {name}')
        deps = task.get('needs', [])
        if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps):
            raise ValueError(f'Invalid dependencies for {name}')
        needs[name] = sorted(set(deps))
        durations[name] = duration
    children = {name: [] for name in tasks}
    degree = {name: len(needs[name]) for name in tasks}
    for name in tasks:
        for dep in needs[name]:
            if dep not in tasks:
                raise ValueError(f'Unknown dependency {dep} for {name}')
            children[dep].append(name)
    ready = [name for name in tasks if degree[name] == 0]
    heapq.heapify(ready)
    order, times, levels, parent = [], {}, {}, {}
    while ready:
        name = heapq.heappop(ready)
        deps = needs[name]
        predecessor = min(deps, key=lambda d: (-times[d]['finish'], d)) if deps else None
        start = times[predecessor]['finish'] if predecessor is not None else 0
        times[name] = {'start': start, 'finish': start + durations[name]}
        parent[name] = predecessor
        levels[name] = 1 + max((levels[d] for d in deps), default=-1)
        order.append(name)
        for child in sorted(children[name]):
            degree[child] -= 1
            if degree[child] == 0:
                heapq.heappush(ready, child)
    if len(order) != len(tasks):
        blocked = sorted(name for name in tasks if degree[name])
        raise ValueError('Cycle blocks tasks: ' + ', '.join(blocked))
    endpoint = min(order, key=lambda n: (-times[n]['finish'], n)) if order else None
    path = []
    node = endpoint
    while node is not None:
        path.append(node)
        node = parent[node]
    layers = [[n for n in order if levels[n] == level] for level in range(max(levels.values(), default=-1) + 1)]
    return {'order': order, 'levels': layers, 'times': times,
            'duration': times[endpoint]['finish'] if endpoint is not None else 0,
            'critical_path': list(reversed(path))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help='JSON task mapping')
    args = parser.parse_args()
    try:
        with open(args.file, encoding='utf-8') as handle:
            tasks = json.load(handle)
        if not isinstance(tasks, dict):
            raise ValueError('Root must be an object')
        result = plan(tasks)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'error: {exc}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
