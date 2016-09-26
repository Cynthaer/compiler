# -*- coding: UTF-8 -*-

import re
import reparse as rep
import collections as col
import operator as op
import itertools
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
    
    def swap_nodes(self, s1, s2):
        if self.start == s1:
            self.start = s2
        elif self.start == s2:
            self.start = s1
        
        if s1 in self.final and s2 not in self.final:
            self.final.remove(s1)
            self.final.add(s2)
        elif s2 in self.final and s1 not in self.final:
            self.final.remove(s2)
            self.final.add(s1)
        
        # helper to get right state
        def st(s):
            if s == s1:
                return s2
            elif s == s2:
                return s1
            else:
                return s

        self.transtable = {
            st(k): [ (c, st(t)) for c, t in translist ]
                for k, translist in self.transtable.items()
        }
    
    def prettify(self):
        """
        Rearranges the nodes to flow more intuitively for humans
        """
                
        # start on 0
        self.swap_nodes(self.start, 0)
        print(self)
        translations = { 0: 0 }
        
        new_transitions = col.defaultdict(list)
        for from_state, transitions in sorted(self.transtable.items()):
            
            if from_state not in translations:
                translations[from_state] = len(translations)
            
            for c, to_state in transitions:
                if to_state not in translations:
                    translations[to_state] = len(translations)
                
                new_transitions[translations[from_state]].append((c, translations[to_state]))
            
            print('\ntranslations')
            pprint.pprint(translations)
            print('\nnew_transitions')
            pprint.pprint(new_transitions)
        
        self.transtable = dict(new_transitions)
        self.final = { translations[s] for s in self.final }
        
    
    def __str__(self):
        output = 'Q: {}\nΣ: {}\nΔ:\n{}\nq0: {}\nF: {}'.format(
            self.get_states(), 
            self.get_alphabet(), 
            pprint.pformat(self.transtable, width=40, indent=4), 
            self.start, 
            self.final
        )

        return output 
    
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
        """
        Uses a worklist algorithm to minimize DFA.
        """
            
        # self.counter = 0
        min_dfa = FSM()
        
        alphabet = self.dfa.get_alphabet()
        
        # [ ( { state, ... },  ) ]
        groups = [
            (self.dfa.final, []), 
            (self.dfa.get_states() - self.dfa.final, [])
        ]
        # print(groups)
        
        i = 0
        while i < len(groups):
            # print('groups', groups)
            
            # group_table format: { from_state: [ (c, to_state), ... ], ... }
            group_table = {}
            for state in groups[i][0]:
                group_table[state] = []
                for c in alphabet:
                    try:
                        to_state = self.dfa.move(state, c).pop()
                    except KeyError:
                        continue
                    
                    for g in groups:
                        if to_state in g[0]:
                            group_table[state].append((c, groups.index(g)))
                
                # have to keep orders consistent so we can group later
                group_table[state].sort()  
            
            sorted_table = sorted(group_table.items(), key=op.itemgetter(1))
            # print('sorted_table', sorted_table)
            new_groups = [
                ({s for s, _ in g}, x)
                for x, g in itertools.groupby(sorted_table, key=op.itemgetter(1))
            ]
            
            groups[i:i+1] = new_groups
            
            if len(new_groups) > 1:
                i = 0
            else:
                i += 1

            # print('group_table', group_table)
            # print('new_groups', new_groups)
            # pprint.pprint(groups)

        # print('final groups', groups)
        
        # final minimized DFA
        min_dfa = FSM()
        for grouped_state in range(len(groups)):
            for transition in groups[grouped_state][1]:
                min_dfa.add_transition(grouped_state, *transition)
            
            # if new state contains previous start state, it is new start state
            if self.dfa.start in groups[grouped_state][0]:
                min_dfa.start = grouped_state
            
            # ditto for final states
            if not self.dfa.final.isdisjoint(groups[grouped_state][0]):
                min_dfa.final.add(grouped_state)
        
        print('before prettify\n', min_dfa)
        
        # make 0 the start node just to look nice
        min_dfa.prettify()
        
        self.dfa = min_dfa

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
    test_regex = '((a|b)(a|bb))*'
    dfa = regex_to_dfa(test_regex)
    print(test_regex)
    print(dfa)

if __name__ == '__main__':
    main()