import random
import time

import numpy as np  # noqas
import pysos  # noqa

from numstore import Dict

items = 99 * 1000 * 1000


def benchmark(module: str, db):
    t = time.time()
    for i in range(items):
        if i % 2 == 0:
            db[i] = str(i)[-1:]
        else:
            db[i] = str(i)[-1:]
    dt = time.time() - t

    print(f"[{module}] write: {int(items / dt)} / second")

    random_keys = [random.randint(0, items - 1) for _ in range(0, 10000)]
    data = []

    t = time.time()
    if isinstance(db, dict):
        for i in random_keys:
            data.append(db.get(i))
    else:
        for i in random_keys:
            data.append(db[i])

    dt = time.time() - t

    print(f"[{module}] reads: {int(10000 / dt)} / second\n")


db_numstore: Dict = Dict(length=8)
benchmark(module="numstore".ljust(10), db=db_numstore)
db_numstore.save()
del db_numstore

db_numpy: np.ndarray = np.empty(items)
benchmark(module="numpy".ljust(10), db=db_numpy)
del db_numpy

db_dict: dict = {}
benchmark(module="dict".ljust(10), db=db_dict)
del db_dict

db_pysos = pysos.Dict("test.db")
benchmark(module="pysos".ljust(10), db=db_pysos)

db_pysos.close()
del db_pysos
