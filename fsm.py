# -*- coding: UTF-8 -*-

import re
import reparse as rep
import collections
import pprint

class FSM(object):
    def __init__(self, transtable=None, start=0, final=None):
        # transitions format: { 0: [(None, 1), ('a', 2)] }
        #                     { s: [(c, t)] }
        self.transtable = transtable or {}
        self.start = start
        
        if final is None:
            self.final = set()
        else:
            try:
                self.final = set(final)
            except TypeError:
                self.final = {final}
                
    def add_transition(self, s, c, t):
        if s not in self.transtable:
            self.transtable[s] = [(c, t)]
        elif (c, t) not in self.transtable[s]:
            self.transtable[s].append((c, t))
    
    def get_states(self):
        states = set()
        for s in self.transtable:
            # all the states with transitions out
            states.add(s)  
            # all the states with transitions in
            states.update([t for c, t in self.transtable[s]])  
        return states
    
    def get_alphabet(self):
        alphabet = set()
        for s in self.transtable:
            alphabet.update([c for c, t in self.transtable[s]])
        
        alphabet.discard(None)
        return alphabet
    
    def move(self, state, symbol):
        result = set()
        if state in self.transtable:
            for c, t in self.transtable[state]:
                if c == symbol:
                    result.add(t)
        return result
        
    def __str__(self):
        output = 'Q: {}\nΣ: {}\nΔ:\n{}\nq0: {}\nF: {}'.format(
            self.get_states(), 
            self.get_alphabet(), 
            pprint.pformat(self.transtable, width=40, indent=4), 
            self.start, 
            self.final
        )

        return output 
        # obj = collections.OrderedDict()
        # obj['Q'] = self.get_states()
        # obj['Σ'] = self.get_alphabet()
        # obj['Δ'] = self.transtable
        # obj['q_0'] = self.start
        # obj['F'] = self.final
        
        # return pprint.pformat(obj)
    
    def __repr__(self):
        return 'FSM({}, {}, {})'.format(self.transtable, self.start, self.final)
        
class RegexNFAConverter(object):
    def __init__(self, regex):
        self.regex = regex
        self.counter = 0  # used to track state
        
        self.tree = self.regex_to_tree(self.regex)
        
        self.fsm = FSM()
    
    def new_state(self):
        state = self.counter
        self.counter += 1
        return state
        
    def regex_to_tree(self, regex):
        return rep.REParser(regex).parse()
    
    def tree_to_nfa(self, tree=None, start_state=None, end_state=None):
        if tree is None:
            tree = self.tree
        
        if start_state is None:
            start_state = self.new_state()
        
        if end_state is None:
            end_state = self.new_state()
            self.fsm.final = {end_state}
        
        if type(tree) is rep.Primitive:
            self.fsm.add_transition(start_state, tree.c, end_state)
            
        elif type(tree) is rep.Star:
            s1 = self.new_state()
            
            # ε-transition to fragment/out
            self.fsm.add_transition(start_state, None, s1)
            self.fsm.add_transition(start_state, None, end_state)
            
            # populate the fragment, loop back to start
            self.tree_to_nfa(tree.a, s1, start_state)
            
        elif type(tree) is rep.Concat:
            s1 = self.new_state()
            
            # first fragment
            self.tree_to_nfa(tree.a, start_state, s1)
            
            # second fragment
            self.tree_to_nfa(tree.b, s1, end_state)
            
        elif type(tree) is rep.Or:
            s1 = self.new_state()
            s2 = self.new_state()
            
            # first branch
            self.fsm.add_transition(start_state, None, s1)
            self.tree_to_nfa(tree.a, s1, end_state)
            
            # second branch
            self.fsm.add_transition(start_state, None, s2)
            self.tree_to_nfa(tree.b, s2, end_state)
        
        return self.fsm
            
class NFADFAConverter(object):
    def __init__(self, nfa):
        self.nfa = nfa
        self.dfa = FSM()
        self.counter = 0
            
    def next_state(self):
        state = self.counter
        self.counter += 1
        return state

    def nfa_to_dfa(self):
        # self.counter = 0
        alphabet = self.nfa.get_alphabet()
        
        # worklist algorithm
        dfa_states = [self.ep_closure({self.nfa.start})]
        self.dfa.first = 0
        
        i = 0
        while i < len(dfa_states):
            s_i = dfa_states[i]
            for c in alphabet:
                s_j = set()
                for nfa_state in s_i:
                    s_j.update(self.ep_closure(self.nfa.move(nfa_state, c)))
                if len(s_j) > 0:
                    if s_j not in dfa_states:
                        dfa_states.append(s_j)
                    to_state = dfa_states.index(s_j)
                    self.dfa.add_transition(i, c, to_state)
            i += 1
        
        self.dfa.final = { 
            dfa_states.index(s) 
            for s in dfa_states 
            if not s.isdisjoint(self.nfa.final) 
        }

        self.minimize_dfa()

        return self.dfa
    
    def minimize_dfa(self):
        # self.counter = 0
        min_dfa = FSM()
        
        alphabet = self.dfa.get_alphabet()
        
        groups = [self.dfa.final, self.dfa.get_states() - self.dfa.final]
        print(groups)
        
        i = 0
        while i < len(groups):
            if len(groups[i]) == 1:
                i += 1
                continue
            
            group_table = {}
            for state in groups[i]:
                print('state: {}'.format(state))
                group_table[state] = {}
                for c in alphabet:
                    to_states = self.dfa.move(state, c)
                    if len(to_states) == 0:
                        continue
                    to_state = to_states.pop()
                    for g in groups:
                        if to_state in g:
                            group_table[state][c] = groups.index(g)
            
            print(group_table)
            print(group_table[1] == group_table[0])
            i += 1

    def ep_closure(self, states):
        # worklist algorithm - track by converting set to dict
        statedict = dict.fromkeys(states)

        while None in statedict.values():
            # find one we haven't touched yet
            for s in statedict:
                if statedict[s] is None:
                    break

            new_states = self.nfa.move(s, None)
            for s_new in new_states:
                statedict.setdefault(s_new)
            statedict[s] = True
            
        return set(statedict.keys())


def regex_to_nfa(regex):
    converter = RegexNFAConverter(regex)    
    nfa = converter.tree_to_nfa()
    return nfa

def regex_to_dfa(regex):
    nfa = regex_to_nfa(regex)
    converter = NFADFAConverter(nfa)
    return converter.nfa_to_dfa()

def main():
    print(regex_to_dfa('(aa*bb*)|ab'))
    
    print()

if __name__ == '__main__':
    main()