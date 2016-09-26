class Parser(object):
    """
    T' -> T$
    T -> R
    T -> aTc
    R ->
    R -> bR
    """
    def __init__(self, tokens=[]):
        self.tokens = list(tokens)
    
    def peek(self):
        return self.tokens[0]
    
    def match(self, c):
        return c == self.peek()
    
    def eat(self, c):
        if self.match(c):
            del self.tokens[0]
        else:
            raise ValueError('Cannot eat token \'{}\', next token is \'{}\'.'.format(c, self.tokens[0]))

            
    def parse_Tpr(self):
        c = self.peek()
        
        first_Tpr = {'a', 'b', '$'}
        
        # unnecessary check, but convenient
        if c not in first_Tpr:
            raise ValueError('No production found for {} in T\''.format(c))
        
        # T' -> T$
        self.parse_T()
        self.eat('$')
    
    def parse_T(self):
        c = self.peek()
        
        follow_T = {'$', 'c'}
        
        # T -> R
        first_R = {'b'}
        nullable_R = True
        
        if c in first_R or (nullable_R and c in follow_T):
            self.parse_R()
            return
        
        # T -> aTc
        first_aTc = {'a'}
        nullable_aTc = False
        
        if c in first_aTc or (nullable_aTc and c in follow_T):
            self.eat('a')
            self.parse_T()
            self.eat('c')
            return
    
    def parse_R(self):
        c = self.peek()
        
        follow_R = {'$', 'c', 'b'}
        
        # R ->
        
        first_ε = set()
        
        # R -> bR

def main():
    p = Parser('c')
    p.parse_Tpr()
    
if __name__ == '__main__':
    main()