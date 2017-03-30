#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2017, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
from builtins import str, map, object, range, zip, sorted
import os
import sys


def read_generalized(fname):
    with open(fname, "r") as f:
        lst = f.read().split()

    def discard_until(mark):
        while lst[0] != mark:
            lst.pop(0)
        lst.pop(0)

    def increase_key(dic, key):
        if key not in dic:
            dic[key] = 1
        else:
            dic[key] += 1

    discard_until("BINTYPES")
    nbtypes = int(lst.pop(0))

    discard_until("ITEMS")
    nitems = int(lst.pop(0))

    bins = []
    discard_until("BINS_SECTIONS")
    Ws, Cs, Ls, Us = [], [], [], []
    for i in range(nbtypes):
        _bid, _capacity, _cost, _l, _u = map(int, lst[:5])
        Ws.append(tuple([_capacity]))
        Cs.append(_cost)
        Ls.append(_l)
        Us.append(_u)
        assert _bid == i
        lst = lst[5:]
    U = -1  # unlimited number of bins

    groups = {}
    discard_until("ITEMS_SECTIONS")
    for i in range(nitems):
        _iid, _volume, _profit, _forced = map(int, lst[:4])
        if _volume not in groups:
            groups[_volume] = []
        groups[_volume].append((_profit, _forced))
        assert _iid == i
        lst = lst[4:]

    grps = list(groups.keys())

    ws, req, opt, prof, dem = [], {}, {}, {}, {}
    I, J = [], {}
    for i, _volume in enumerate(grps):
        I.append(i)
        J[i] = [0]  # only one incarnation per type
        ws.append([(_volume,)])
        req[i], opt[i] = [], []
        for l, (_profit, _forced) in enumerate(groups[_volume]):
            if _forced:
                req[i].append(l)
            else:
                opt[i].append(l)
            prof[i, l] = _profit
            dem[i, l] = 1

    return (Ws, Cs, Ls, Us, U, ws, I, J, dem, prof, req, opt)


def main():
    """Example: Generalized Bin Packing Problem."""
    from pyvpsolver.solvers import genvpsolver
    os.chdir(os.path.dirname(__file__) or os.curdir)
    from glob import glob
    from time import time

    path = "instances/MAUROBALDI/"
    folders = ["TIPO0", "TIPO1", "TIPO2", "TIPO3"]
    # folders = ["TIPO0", "TIPO0FORZATI", "TIPO1", "TIPO2", "TIPO3", "TIPO4"]
    # folders = ["TIPO3"]
    for folder in folders:
        print(">", folder)
        log_folder = "tmp/logs/{}".format(folder)
        try:
            os.makedirs(log_folder)
        except OSError:
            pass
        for instance in sorted(glob(path+folder+"/prob_*.txt")):
            print(">>", folder, instance)
            geninst = read_generalized(instance)
            stdout_org = sys.stdout
            fname = instance[instance.rfind("/")+1:]
            log_file = "{}/{}".format(log_folder, fname)
            with open(log_file, "w") as f:
                sys.stdout = f
                t0 = time()
                obj, lst_sol = genvpsolver.solve(
                    geninst, script="vpsolver_gurobi.sh",
                    script_options="""
                    Threads=1 Presolve=1 Method=2
                    MIPGap=0 MIPGapAbs=0.99999 Seed=1234 TimeLimit=300
                    """,
                    verbose=True
                )
                genvpsolver.print_solution(obj, lst_sol, fout=f)
                t1 = time()
            sys.stdout = stdout_org
            print("### {} {} {} ({})".format(folder, fname, t1-t0, log_file))


if __name__ == "__main__":
    main()
