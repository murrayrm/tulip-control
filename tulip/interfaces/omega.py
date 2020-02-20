# Copyright by California Institute of Technology
# All rights reserved. See LICENSE file at:
# https://github.com/tulip-control/tulip-control
"""Interface to `omega` package.

`omega` constructs symbolic transducers,
represented as binary decision diagrams.
This module applies enumeration,
to return enumerated transducers.

U{https://pypi.python.org/pypi/omega}
"""
from __future__ import absolute_import
from __future__ import print_function

import logging
import time

try:
    import omega
    from omega.logic import bitvector as bv
    from omega.games import gr1
    from omega.symbolic import temporal as trl
    from omega.games import enumeration as enum
except ImportError:
    omega = None
import networkx as nx


log = logging.getLogger(__name__)


def is_realizable(spec, use_cudd=False):
    """Return `True` if, and only if, realizable.

    See `synthesize_enumerated_streett` for more details.
    """
    aut = _grspec_to_automaton(spec)
    t0 = time.time()
    z, _, _ = gr1.solve_streett_game(aut)
    t1 = time.time()
    return gr1.is_realizable(z, aut)


def synthesize_enumerated_streett(spec, use_cudd=False):
    """Return transducer enumerated as a graph.

    @type spec: `tulip.spec.form.GRSpec`
    @param use_cudd: efficient BDD computations with `dd.cudd`
    @rtype: `networkx.DiGraph`
    """
    aut = _grspec_to_automaton(spec)
    assert aut.action['sys'] != aut.false
    t0 = time.time()
    z, yij, xijk = gr1.solve_streett_game(aut)
    t1 = time.time()
    # unrealizable ?
    if not gr1.is_realizable(z, aut):
        print('WARNING: unrealizable')
        return None
    u = gr1.make_streett_transducer(z, yij, xijk, aut)
    aut.init['env'] = aut.init['impl_env']
    aut.init['sys'] = aut.init['impl_sys']
    aut.action['sys'] = u
    t2 = time.time()
    assert u != aut.false
    g = enum.action_to_steps(aut, qinit=aut.qinit)
    h = _strategy_to_state_annotated(g, aut)
    del u, yij, xijk
    t3 = time.time()
    log.info((
        'Winning set computed in {win} sec.\n'
        'Symbolic strategy computed in {sym} sec.\n'
        'Strategy enumerated in {enu} sec.').format(
            win=t1 - t0,
            sym=t2 - t1,
            enu=t3 - t2))
    return h


def is_circular(spec, use_cudd=False):
    """Return `True` if trivial winning set non-empty.

    @type spec: `tulip.spec.form.GRSpec`
    @param use_cudd: efficient BDD computations with `dd.cudd`
    @rtype: `bool`
    """
    aut = _grspec_to_automaton(spec)
    triv, t = gr1.trivial_winning_set(aut)
    return triv != t.bdd.false


def _int_bounds(aut):
    """Create care set for enumeration.

    @type aut: `omega.symbolic.symbolic.Automaton`
    @return: node in a `dd.bdd.BDD`
    @rtype: `int`
    """
    int_types = {'int', 'saturating', 'modwrap'}
    bdd = aut.bdd
    u = bdd.true
    for var, d in aut.vars.items():
        t = d['type']
        if t == 'bool':
            continue
        assert t in int_types, t
        dom = d['dom']
        p, q = dom
        e = "({p} <= {var}) & ({var} <= {q})".format(
            p=p, q=q, var=var)
        v = aut.add_expr(e)
        u = bdd.apply('and', u, v)
    return u


def _strategy_to_state_annotated(g, aut):
    """Move annotation to `dict` as value of `'state'` key.

    @type g: `nx.DiGraph`
    @type: aut: `omega.symbolic.symbolic.Automaton`
    @rtype: `nx.DiGraph`
    """
    h = nx.DiGraph()
    for u, d in g.nodes(data=True):
        dvars = {k: d[k] for k in d if k in aut.vars}
        h.add_node(u, state=dvars)
    for u, v in g.edges():
        h.add_edge(u, v)
    h.initial_nodes = set(g.initial_nodes)
    return h


def _grspec_to_automaton(g):
    """Return `omega.symbolic.temporal.Automaton` from `GRSpec`.

    @type g: `tulip.spec.form.GRSpec`
    @rtype: `omega.symbolic.temporal.Automaton`
    """
    if omega is None:
        raise ImportError(
            'Failed to import package `omega`.')
    a = trl.Automaton()
    d = dict(g.env_vars)
    d.update(g.sys_vars)
    for k, v in d.items():
        if v in ('boolean', 'bool'):
            r = 'bool'
        elif isinstance(v, list):
            # string var -> integer var
            r = (0, len(v) - 1)
        elif isinstance(v, tuple):
            r = v
        else:
            raise ValueError(
                'unknown variable type: {v}'.format(v=v))
        d[k] = r
    g.str_to_int()
    
    # reverse mapping by `synth.strategy2mealy`
    a.declare_variables(**d)
    a.varlist.update(env=list(g.env_vars.keys()), sys=list(g.sys_vars.keys()))

    f = g._bool_int.__getitem__
    a.init['env'] = " & ".join("( %s )" % f(ei) for ei in g.env_init) if len(g.env_init) > 0 else "TRUE"
    a.init['sys'] = " & ".join("( %s )" % f(si) for si in g.sys_init) if len(g.sys_init) > 0 else "TRUE"
    a.action['env'] = " & ".join("( %s )" % f(es) for es in g.env_safety) if len(g.env_safety) > 0 else "TRUE"
    a.action['sys'] = " & ".join("( %s )" % f(ss) for ss in g.sys_safety) if len(g.sys_safety) > 0 else "TRUE"

    w1 = ['!({s})'.format(s=s) for s in map(f, g.env_prog)] if len(g.env_prog) > 0 else ["FALSE"]
    w2 = [f(sp) for sp in g.sys_prog] if len(g.sys_prog) > 0 else ["TRUE"]
    a.win['<>[]'] = a.bdds_from(*w1)
    a.win['[]<>'] = a.bdds_from(*w2)

    a.moore = g.moore
    a.plus_one = g.plus_one
    a.qinit = g.qinit

    return a
