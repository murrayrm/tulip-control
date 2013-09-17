# Copyright (c) 2013 by California Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the California Institute of Technology nor
#    the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL CALTECH
# OR THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
Automata Module
"""
from collections import Iterable, OrderedDict
from pprint import pformat
#import warnings

from labeled_graphs import LabeledStateDiGraph
from labeled_graphs import vprint, prepend_with, str2singleton
from mathset import MathSet, SubSet, PowerSet, dprint
import transys

hl = 60 *'-'

# future: may become an abc
class FiniteStateAutomaton(LabeledStateDiGraph):
    """Generic automaton.
    
    It has:
        - states
        - states.initial
        - states.aceepting (type depends on automaton flavor)
        - alphabet = set of input letters (labeling edges)
            (possibly based on atomic propositions (AP),
             meaning it is the powerset of some AP set)
        - is_accepted, for testing input words
    
    If C{atomic_proposition_based=False},
    then the alphabet is represented by a set.
    
    If C{atomic_proposition_based=True},
    the the alphabet is represented by a powerset 2^AP.
    
    note
    ----
    Automata represent languages in a way suitable for
    testing if a given trace is a member of the language.
    So an automaton operates in acceptor mode,
    i.e., testing input words.
    
    The represented language is not readily accessible,
    because its generation requires solving a search problem.
    This is search problem is the usual model checking,
    assuming a transition system with a complete digraph.
    
    For constructively representing a language,
    use a Finite Transition System.
    A transition system operates only in generator mode,
    producing a language (possibly non-deterministically).
    
    For controllers, use a Finite State Machine,
    because it maps input words (input port valuations) to
    outputs (output port valuations).
    
    see also
    --------    
    NFA, DFA, BA, RabinAutomaton, DRA, StreettAutomaton,
    MullerAutomaton, ParityAutomaton
    """
    def __init__(
            self, name='', mutable=False, deterministic=False,
            accepting_states_type=SubSet,
            atomic_proposition_based=True,
        ):
        # edge labeling
        if atomic_proposition_based:
            self.atomic_proposition_based = True
            alphabet = PowerSet([])
        else:
            self.atomic_proposition_based = False
            alphabet = set()
        
        self._transition_label_def = OrderedDict([
            ['in_alphabet', alphabet]
        ])
        self.alphabet = self._transition_label_def['in_alphabet']
        
        LabeledStateDiGraph.__init__(
            self, mutable=mutable,
            accepting_states_type=accepting_states_type
        )
        
        # used before label value
        self._transition_dot_label_format = {'in_alphabet':'',
                                                'type?label':'',
                                                'separator':'\\n'}
        
        self.dot_node_shape = {'normal':'circle',
                               'accepting':'doublecircle'}
        self.default_export_fname = 'fsa'
        self.automaton_type = 'Finite State Automaton'
    
    def __repr__(self):
        s = hl +'\n' +self.automaton_type +': '
        s += self.name +'\n' +hl +'\n'
        s += 'States:\n'
        s += pformat(self.states(data=False), indent=3) +2*'\n'
        s += 'Initial States:\n'
        s += pformat(self.states.initial, indent=3) +2*'\n'
        s += 'Accepting States:\n'
        s += pformat(self.states.accepting, indent=3) +2*'\n'
        
        if self.atomic_proposition_based:
            s += 'Input Alphabet Letters (\in 2^AP):\n\t'
        else:
            s += 'Input Alphabet Letters:\n\t'
        s += str(self.alphabet) +2*'\n'
        s += 'Transitions & labeling w/ Input Letters:\n'
        s += pformat(self.transitions(labeled=True), indent=3)
        s += '\n' +hl +'\n'
        
        return s
    
    def __str__(self):
        return self.__repr__()
    
    def is_accepted(self, word):
        """Check if automaton accepts input word.
        """
        print('Implemented by subclasses')
    
    def simulate(self, initial_state, word):
        """Return an Automaton Simulation.
        """
        print('Implemented by subclasses')

class NFA(FiniteStateAutomaton):
    """Finite-word finite-state automaton.
    
    Determinism can be enforced by optional argument
    when creating transitions.
    """
    def __init__(self, name='', mutable=False,
                 atomic_proposition_based=True,
                 deterministic=False):
        FiniteStateAutomaton.__init__(
            self, name, mutable, deterministic,
            atomic_proposition_based=atomic_proposition_based
        )
        self.automaton_type = 'Non-Deterministic Finite Automaton'
    
    def is_accepted(self, word):
        """Check if automaton accepts finite input word.
        """
        raise NotImplementedError

class DFA(NFA):
    """Finite-word finite-state automaton.
    
    Determinism can be enforced by optional argument
    when creating transitions.
    """
    def __init__(self, name='', mutable=False,
                 atomic_proposition_based=True):
        NFA.__init__(
            self, name, mutable, deterministic=True,
            atomic_proposition_based=atomic_proposition_based,
        )
        self.automaton_type = 'Deterministic Finite Automaton'

def nfa2dfa():
    """Determinize NFA.
    """
    raise NotImplementedError
    
def dfa2nfa(dfa):
    """Copy DFA to an NFA, so remove determinism restriction.
    """
    nfa = dfa.copy()
    nfa.transitions._deterministic = False
    nfa.automaton_type = 'Non-Deterministic Finite Automaton'
    return nfa

class OmegaAutomaton(FiniteStateAutomaton):
    def __init__(self, *args, **kwargs):
        FiniteStateAutomaton.__init__(self, *args, **kwargs)

class BuchiAutomaton(OmegaAutomaton):
    def __init__(
            self, name='', mutable=False,
            deterministic=False,
            atomic_proposition_based=True
        ):
        OmegaAutomaton.__init__(
            self, name, mutable, deterministic,
            atomic_proposition_based=atomic_proposition_based
        )
        self.automaton_type = 'Buchi Automaton'
    
    def __add__(self, other):
        """Union of two automata, with equal states identified.
        """
        raise NotImplementedError
    
    def __mul__(self, ts_or_ba):
        return self.sync_prod(ts_or_ba)
    
    def __or__(self, ba):
        return self.async_prod(ba)
        
    def _ba_ba_sync_prod(self, ba2):
        #ba1 = self
        
        raise NotImplementedError
        #TODO BA x BA sync prod algorithm

    def sync_prod(self, ts_or_ba):
        """Synchronous product between (BA, TS), or (BA1, BA2).
        
        The result is always a Buchi Automaton:
        
            - If C{ts_or_ba} is a Finite Transition System TS,
                then return the synchronous product BA * TS.
                
                The accepting states of BA * TS are those which
                project on accepting states of BA.
            
            - If C{ts_or_ba} is a Buchi Automaton BA2,
                then return the synchronous product BA * BA2.
        
                The accepting states of BA * BA2 are those which
                project on accepting states of both BA and BA2.
        
                This definition of accepting set extends
                Def.4.8, p.156 [Baier] to NBA.
        
        caution
        -------
        This method includes semantics for true\in\Sigma (p.916, [Baier]),
        so there is a slight overlap with logic grammar.
        In other words, not completely isolated from logics.
        
        see also
        --------        
        ts_ba_sync_prod
        
        @param ts_or_ba: other with which to take synchronous product
        @type ts_or_ba: FiniteTransitionSystem or BuchiAutomaton
        
        @return: self * ts_or_ba
        @rtype: BuchiAutomaton
        """
        if isinstance(ts_or_ba, BuchiAutomaton):
            return self._ba_ba_sync_prod(ts_or_ba)
        elif isinstance(ts_or_ba, transys.FiniteTransitionSystem):
            ts = ts_or_ba
            return _ba_ts_sync_prod(self, ts)
        else:
            raise Exception('ts_or_ba should be an FTS or a BA.\n'+
                            'Got type: ' +str(ts_or_ba) )
    
    def is_accepted(self, prefix, suffix):
        """Check if given infinite word over alphabet \Sigma is accepted.
        """

class BA(BuchiAutomaton):
    """Alias to BuchiAutomaton.
    """
    def __init__(self, **args):
        BuchiAutomaton.__init__(self, **args)

def tuple2ba(S, S0, Sa, Sigma_or_AP, trans, name='ba', prepend_str=None,
             atomic_proposition_based=True, verbose=False):
    """Create a Buchi Automaton from a tuple of fields.
    
    see also
    --------
    L{tuple2fts}

    @type ba_tuple: tuple
    @param ba_tuple: defines Buchi Automaton by a tuple (Q, Q_0, Q_F,
        \\Sigma, trans) (maybe replacing \\Sigma by AP since it is an
        AP-based BA ?)  where:

            - Q = set of states
            - Q_0 = set of initial states, must be \\subset S
            - Q_a = set of accepting states
            - \\Sigma = alphabet
            - trans = transition relation, represented by list of triples:
              [(from_state, to_state, guard), ...]
              where guard \\in \\Sigma.

    @param name: used for file export
    @type name: str
    """
    # args
    if not isinstance(S, Iterable):
        raise TypeError('States S must be iterable, even for single state.')
    
    if not isinstance(S0, Iterable) or isinstance(S0, str):
        S0 = [S0]
    
    if not isinstance(Sa, Iterable) or isinstance(Sa, str):
        Sa = [Sa]
    
    # comprehensive names
    states = S
    initial_states = S0
    accepting_states = Sa
    alphabet_or_ap = Sigma_or_AP
    transitions = trans
    
    # prepending states with given str
    if prepend_str:
        vprint('Given string:\n\t' +str(prepend_str) +'\n' +
               'will be prepended to all states.', verbose)
    states = prepend_with(states, prepend_str)
    initial_states = prepend_with(initial_states, prepend_str)
    accepting_states = prepend_with(accepting_states, prepend_str)
    
    ba = BA(name=name, atomic_proposition_based=atomic_proposition_based)
    
    ba.states.add_from(states)
    ba.states.initial |= initial_states
    ba.states.accepting |= accepting_states
    
    if atomic_proposition_based:
        ba.alphabet.math_set |= alphabet_or_ap
    else:
        ba.alphabet.add(alphabet_or_ap)
    
    for transition in transitions:
        (from_state, to_state, guard) = transition
        [from_state, to_state] = prepend_with([from_state, to_state],
                                              prepend_str)
        # convention
        if atomic_proposition_based:
            guard = str2singleton(guard)
        ba.transitions.add_labeled(from_state, to_state, guard)
    
    return ba

def _ba_ts_sync_prod(buchi_automaton, transition_system):
    """Construct Buchi Automaton equal to synchronous product TS x NBA.
    
    returns
    -------
    C{prod_ba}, the product Buchi Automaton.
    
    see also
    --------
    _ts_ba_sync_prod, BuchiAutomaton.sync_prod
    """
    (prod_ts, persistent) = _ts_ba_sync_prod(
        transition_system, buchi_automaton
    )
    
    prod_name = buchi_automaton.name +'*' +transition_system.name
    
    if prod_ts.states.mutants:
        mutable = True
    else:
        mutable = False
    
    prod_ba = BuchiAutomaton(name=prod_name, mutable=mutable)
    
    # copy S, S0, from prod_TS-> prod_BA
    prod_ba.states.add_from(prod_ts.states() )
    prod_ba.states.initial |= prod_ts.states.initial()
    print('initial:\n\t' +str(prod_ts.states.initial) )
    # accepting states = persistent set
    prod_ba.states.accepting |= persistent
    
    # copy edges, translating transitions,
    # i.e., changing transition labels
    if buchi_automaton.atomic_proposition_based:
        # direct access, not the inefficient
        #   prod_ba.alphabet.add_from(buchi_automaton.alphabet() ),
        # which would generate a combinatorially large alphabet
        prod_ba.alphabet.math_set |= buchi_automaton.alphabet.math_set
    else:
        msg ="""
            Buchi Automaton must be Atomic Proposition-based,
            otherwise the synchronous product is not well-defined.
            """
        raise Exception(msg)
    
    for (from_state_id, to_state_id) in prod_ts.transitions():
        # prject prod_TS state to TS state
        
        from_state = prod_ts.states._int2mutant(from_state_id)
        to_state = prod_ts.states._int2mutant(to_state_id)
        
        ts_to_state = to_state[0]
        msg = 'prod_TS: to_state =\n\t' +str(to_state) +'\n'
        msg += 'TS: ts_to_state =\n\t' +str(ts_to_state)
        dprint(msg)
        
        state_label_pairs = transition_system.states.find(ts_to_state)
        (ts_to_state_, transition_label_dict) = state_label_pairs[0]
        transition_label_value = transition_label_dict['ap']
        prod_ba.transitions.add_labeled(
            from_state, to_state, transition_label_value
        )
    
    return prod_ba

def _ts_ba_sync_prod(transition_system, buchi_automaton):
    """Construct transition system for the synchronous product TS * BA.
    
    Def. 4.62, p.200 [Baier]
    
    erratum
    -------
    note the erratum: P_{pers}(A) is ^_{q\in F} !q, verified from:
        http://www-i2.informatik.rwth-aachen.de/~katoen/errata.pdf
    
    see also
    --------
    _ba_ts_sync_prod, FiniteTransitionSystem.sync_prod
    
    @return: C{(product_ts, persistent_states)}, where:
        - C{product_ts} is the synchronous product TS * BA
        - C{persistent_states} are those in TS * BA which
            project on accepting states of BA.
    @rtype:
        - C{product_TS} is a FiniteTransitionSystem
        - C{persistent_states} is the set of states which project
            on accepting states of the Buchi Automaton BA.
    """
    def convert_ts2ba_label(state_label_dict):
        """Replace 'ap' key with 'in_alphabet'.
        
        @param state_label_dict: FTS state label, its value \\in 2^AP
        @type state_label_dict: dict {'ap' : state_label_value}
        
        @return: BA edge label, its value \\in 2^AP
            (same value with state_label_dict)
        @rtype: dict {'in_alphabet' : edge_label_value}
            Note: edge_label_value is the BA edge "guard"
        """
        dprint('Ls0:\t' +str(state_label_dict) )
        
        (s0_, label_dict) = state_label_dict[0]
        Sigma_dict = {'in_alphabet': label_dict['ap'] }
        
        dprint('State label of: ' +str(s0) +', is: ' +str(Sigma_dict) )
        
        return Sigma_dict
    
    if not isinstance(transition_system, transys.FiniteTransitionSystem):
        msg = 'transition_system not transys.FiniteTransitionSystem.\n'
        msg += 'Actual type passed: ' +str(type(transition_system) )
        raise TypeError(msg)
    
    if not isinstance(buchi_automaton, BuchiAutomaton):
        msg = 'transition_system not transys.BuchiAutomaton.\n'
        msg += 'Actual type passed: ' +str(type(buchi_automaton) )
        raise TypeError(msg)
    
    if not buchi_automaton.atomic_proposition_based:
        msg = """Buchi automaton not stored as Atomic Proposition-based.
                synchronous product with Finite Transition System
                is not well-defined."""
        raise Exception(msg)
    
    fts = transition_system
    ba = buchi_automaton
    
    prodts_name = fts.name +'*' +ba.name
    
    if fts.states.mutants or ba.states.mutants:
        mutable = True
    else:
        mutable = False
    
    # using set() destroys order
    prodts = transys.FiniteTransitionSystem(
        name=prodts_name, mutable=mutable
    )
    prodts.states.add_from(set() )
    prodts.atomic_propositions.add_from(ba.states() )
    prodts.actions.add_from(fts.actions)

    # construct initial states of product automaton
    s0s = fts.states.initial()
    q0s = ba.states.initial()
    
    accepting_states_preimage = MathSet()
    
    dprint(hl +'\n' +' Product TS construction:\n' +hl +'\n')
    for s0 in s0s:
        dprint('Checking initial state:\t' +str(s0) )
        
        Ls0 = fts.states.find(s0)
        
        # desired input letter for BA
        Sigma_dict = convert_ts2ba_label(Ls0)
        
        for q0 in q0s:
            enabled_ba_trans = ba.transitions.find(
                [q0], desired_label=Sigma_dict
            )
            
            # q0 blocked ?
            if not enabled_ba_trans:
                dprint('blocked q0 = ' +str(q0) )
                continue
            
            # which q next ?     (note: curq0 = q0)
            dprint('enabled_ba_trans = ' +str(enabled_ba_trans) )
            for (curq0, q, sublabels) in enabled_ba_trans:
                new_sq0 = (s0, q)                
                prodts.states.add(new_sq0)
                prodts.states.initial.add(new_sq0)
                prodts.states.label(new_sq0, {q} )
                
                # accepting state ?
                if q in ba.states.accepting:
                    accepting_states_preimage.add(new_sq0)
    
    dprint(prodts)
    
    # start visiting reachable in DFS or BFS way
    # (doesn't matter if we are going to store the result)    
    queue = MathSet(prodts.states.initial() )
    visited = MathSet()
    while queue:
        sq = queue.pop()
        visited.add(sq)
        (s, q) = sq
        
        dprint('Current product state:\n\t' +str(sq) )
        
        # get next states
        next_ss = fts.states.post(s)
        next_sqs = MathSet()
        for next_s in next_ss:
            dprint('Next state:\n\t' +str(next_s) )
            
            Ls = fts.states.find(next_s)
            if not Ls:
                raise Exception(
                    'No AP label for FTS state: ' +str(next_s) +
                     '\n Did you forget labeing it ?'
                )
            
            Sigma_dict = convert_ts2ba_label(Ls)
            dprint("Next state's label:\n\t" +str(Sigma_dict) )
            
            enabled_ba_trans = ba.transitions.find(
                [q], desired_label=Sigma_dict
            )
            dprint('Enabled BA transitions:\n\t' +
                   str(enabled_ba_trans) )
            
            if not enabled_ba_trans:
                continue
            
            for (q, next_q, sublabels) in enabled_ba_trans:
                new_sq = (next_s, next_q)
                next_sqs.add(new_sq)
                dprint('Adding state:\n\t' +str(new_sq) )
                
                prodts.states.add(new_sq)
                
                if next_q in ba.states.accepting:
                    accepting_states_preimage.add(new_sq)
                    dprint(str(new_sq) +' contains an accepting state.')
                
                prodts.states.label(new_sq, {next_q} )
                
                dprint('Adding transitions:\n\t' +str(sq) +
                       '--->' +str(new_sq) )
                
                # is fts transition labeled with an action ?
                ts_enabled_trans = fts.transitions.find(
                    [s], to_states=[next_s],
                    desired_label='any', as_dict=False
                )
                for (from_s, to_s, sublabel_values) in ts_enabled_trans:
                    assert(from_s == s)
                    assert(to_s == next_s)
                    dprint('Sublabel value:\n\t' +str(sublabel_values) )
                    
                    # labeled transition ?
                    if not sublabel_values:
                        prodts.transitions.add(sq, new_sq)
                    else:
                        #TODO open FTS
                        prodts.transitions.add_labeled(
                            sq, new_sq, sublabel_values[0]
                        )
        
        # discard visited & push them to queue
        new_sqs = MathSet()
        for next_sq in next_sqs:
            if next_sq not in visited:
                new_sqs.add(next_sq)
                queue.add(next_sq)
    
    return (prodts, accepting_states_preimage)

def ba2dra():
    """Buchi to Deterministic Rabin Automaton converter.
    """
    raise NotImplementedError

def ba2ltl():
    """Buchi Automaton to Linear Temporal Logic formula converter.
    """
    raise NotImplementedError

class RabinPairs(object):
    """Acceptance pairs for Rabin automaton.
    
    Each pair defines an acceptance condition.
    A pair (L, U) comprises of:
        - a set L of "good" states
        - a set U of "bad" states
    L,U must each be a subset of States.
    
    A run: (q0, q1, ...) is accepted if for at least one Rabin Pair,
    it in intersects L an inf number of times, but U only finitely.
    
    Internally a list of 2-tuples of SubSet objects is maintained:
        [(L1, U1), (L2, U2), ...]
    where: Li, Ui, are SubSet objects, with superset
    the Rabin automaton's States.
    
    caution
    -------
    Here and in ltl2dstar documentation L denotes a "good" set.
    [Baier 2008] denote the a "bad" set with L.
    To avoid ambiguity, attributes: .good, .bad were used here.
    
    example
    -------
    >>> dra = RabinAutomaton()
    >>> dra.states.add_from([1, 2, 3] )
    >>> dra.states.accepting.add([1], [2] )
    >>> dra.states.accepting
    
    >>> dra.states.accepting.good(1)
    
    >>> dra.states.accepting.bad(1)
    
    see also
    --------
    RabinAutomaton
    Def. 10.53, p.801, [Baier 2008]
    ltl2dstar documentation
    """
    def __init__(self, automaton_states):
        self._states = automaton_states
        self._pairs = []
    
    def __repr__(self):
        s = 'L = Good states, U = Bad states\n' +30*'-' +'\n'
        for index, (good, bad) in enumerate(self._pairs):
            s += 'Pair: ' +str(index) +', L = ' +str(good)
            s += ', U = ' +str(bad) +'\n'
        return s
    
    def __str__(self):
        return self.__repr__()
    
    def __getitem__(self, index):
        return self._pairs[index]
    
    def __iter__(self):
        return iter(self._pairs)
    
    def __call__(self):
        """Get list of 2-tuples (L, U) of good-bad sets of states.
        """
        return list(self._pairs)
    
    def add(self, good_states, bad_states):
        """Add new acceptance pair (L, U).
        
        see also
        --------
        remove, add_states, good, bad
        
        @param good_states: set L of good states for this pair
        @type good_states: container of valid states
        
        @param bad_states: set U of bad states for this pair
        @type bad_states: container of valid states
        """
        good_set = SubSet(self._states)
        good_set |= good_states
        
        bad_set = SubSet(self._states)
        bad_set |= bad_states
        
        self._pairs.append((good_set, bad_set) )
    
    def remove(self, good_states, bad_states):
        """Delete pair (L, U) of good-bad sets of states.
        
        note
        ----
        Removing a pair which is not last changes
        the indices of all other pairs, because internally
        a list is used.
        
        The sets L,U themselves (good-bad) are required
        for the deletion, instead of an index, to prevent
        acceidental deletion of an unintended pair.
        
        Get the intended pair using __getitem__ first
        (or in any other way) and them call remove.
        If the pair is corrent, then the removal will
        be successful.
        
        see also
        --------
        add
        
        @param good_states: set of good states of this pair
        @type good_states: 
        """
        good_set = SubSet(self._states)
        good_set |= good_states
        
        bad_set = SubSet(self._states)
        bad_set |= bad_states
        
        self._pairs.remove((good_set, bad_set) )
    
    def add_states(self, pair_index, good_states, bad_states):
        try:
            self._pairs[pair_index][0].add_from(good_states)
            self._pairs[pair_index][1].add_from(bad_states)
        except IndexError:
            raise Exception("A pair with pair_index doesn't exist.\n" +
                            'Create a new one by callign .add.')
    
    def good(self, index):
        """Return set L of "good" states for this pair.
        
        @param index: number of Rabin acceptance pair
        @type index: int <= current total number of pairs
        """
        return self._pairs[index][0]
    
    def bad(self, index):
        """Return set U of "bad" states for this pair.
        
        @param index: number of Rabin acceptance pair
        @type index: int <= current total number of pairs
        """
        return self._pairs[index][1]
    
    def has_superset(self, superset):
        """Return true if the given argument is the superset.
        """
        return superset is self._states

class RabinAutomaton(OmegaAutomaton):
    """Rabin automaton.
    
    see also
    --------
    DRA, BuchiAutomaton
    """    
    def __init__(self, name='', mutable=False, deterministic=False,
                 atomic_proposition_based=False):
        OmegaAutomaton.__init__(
            self,  name, mutable, deterministic,
            RabinPairs, atomic_proposition_based
        )
        self.automaton_type = 'Rabin Automaton'
    
    def is_accepted(self, word):
        raise NotImplementedError

class DRA(RabinAutomaton):
    """Deterministic Rabin Automaton.
    
    see also
    --------
    RabinAutomaton
    """
    def __init__(self, name='', mutable=False,
                 atomic_proposition_based=True):
        RabinAutomaton.__init__(
            self, name, mutable, deterministic=True,
            atomic_proposition_based=atomic_proposition_based
        )
        self.automaton_type = 'Deterministic Rabin Automaton'

class StreettAutomaton(OmegaAutomaton):
    """Omega-automaton with Streett acceptance condition.
    """
    def is_accepted(self, word):
        raise NotImplementedError

class MullerAutomaton(OmegaAutomaton):
    """Omega-automaton with Muller acceptance condition.
    """
    def is_accepted(self, word):
        raise NotImplementedError

class ParityAutomaton(OmegaAutomaton):
    """Omega-automaton with Parity acceptance condition.
    """
    def is_accepted(self, word):
        raise NotImplementedError