"""Die festen Instanzen der Vergleiche für test_claims.py, parallel gerechnet (ein Prozess je Kern, höchstens vier) und je Größe nur einmal.

Zeiten stehen in den Zeilen, aber nie in den Tests; die Parallelität ändert nur die gemessenen Sekunden."""

import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor

import syb_constants as C
import syb_evaluation as E

_SERIES: dict = {}
_STRUCT: list = []


def _workers() -> int:
    return max(1, min(4, os.cpu_count() or 1))


def _series_job(job):
    return E.series_row(*job)


def _struct_job(job):
    return E.struct_row(*job)


def _map(fn, jobs):
    with ProcessPoolExecutor(max_workers=_workers(), mp_context=multiprocessing.get_context("spawn")) as ex:
        return list(ex.map(fn, jobs, chunksize=1))


def series_rows(n: int) -> list:
    """Alle Zeilen der Größe `n` (sechs Familien) in der Reihenfolge von `E.series_jobs`."""
    if n not in _SERIES:
        _SERIES[n] = _map(_series_job, E.series_jobs(n))
    return _SERIES[n]


def struct_rows() -> list:
    """Die 16 Instanzen der symmetrischen Familien (Familie, Größe), die größten zuerst gestartet."""
    if not _STRUCT:
        jobs = [(k, n) for k in C.SYM_FAMILIES for n in C.STRUCT_SIZES]
        order = sorted(range(len(jobs)), key=lambda i: -jobs[i][1] * (3 if jobs[i][0] == "bipartite" else 1))
        done = dict(zip(order, _map(_struct_job, [jobs[i] for i in order])))
        _STRUCT.extend(done[i] for i in range(len(jobs)))
    return _STRUCT
