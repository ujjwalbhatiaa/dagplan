# dagplan

A dependency-aware task planner in pure Python. Given a JSON task graph, it returns a deterministic topological order, parallel dependency levels, earliest start/finish times, total duration and one critical path.

## Run

Python 3.10 or later, no packages required.

```sh
python dagplan.py example.json
python -m unittest -v
```

Input maps task names to objects. `duration` defaults to 1 and must be a finite nonnegative number. `needs` defaults to an empty list. Repeated dependencies count once. Unknown dependencies and cycles produce an error and exit code 2.

```json
{"build": {"duration": 3}, "test": {"needs": ["build"], "duration": 2}}
```

The example finishes at time 5, with critical path `build -> test`.

## Model and limits

Uses Kahn's topological sorting with a heap for deterministic tie-breaking. Earliest finish times use dynamic programming over the DAG. Assumes unlimited workers, no resource contention, no working-hour calendar and no task interruption. Levels show dependency depth, not fixed-time execution batches. A cycle error lists blocked nodes, which may include downstream tasks as well as cycle members. Tied critical paths use alphabetical predecessor and endpoint choices.

The test suite includes 12 tests, including all 64 forward-edge DAGs on four nodes checked against independent path enumeration. This is a small educational scheduling tool, not a production resource scheduler.
