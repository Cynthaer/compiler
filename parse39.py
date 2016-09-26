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
        
        first_Tpr = ('a', 'b', '$')
        
        if c not in first_Tpr:
            raise ValueError('No production found for {} in T\''.format(c))
        # T' -> T$
        self.parseT()
        self.eat('$')
    
    def parseT(self):
        c = self.peek()
        
        # T -> R
        # T -> aTc

def main():
    p = Parser('c')
    p.parse_Tpr()
    
if __name__ == '__main__':
    main()