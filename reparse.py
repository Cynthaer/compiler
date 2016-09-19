# <regex> ::= <term> { '|' <regex> }
# 
# <term> ::= { <factor> }
# 
# <factor> ::= <base> { '*' }
# 
# <base> ::= <char>
#          | '\' <char>
#          | '(' <regex> ')'

class RegEx(object):
    def __init__(self):
        pass
    
    def __iter__(self):
        return iter(())
    
    def __str__(self):
        return '\'\''
    
    def __repr__(self):
        return 'RegEx()'

class Or(RegEx):
    def __init__(self, a, b):
        super(Or, self).__init__()
        self.a = a
        self.b = b
    
    def __str__(self):
        return '(|, {}, {})'.format(self.a, self.b)
    
    def __repr__(self):
        return 'Or({}, {})'.format(self.a, self.b)
    
    def __iter__(self):
        return iter(('|', tuple(self.a), tuple(self.b)))

class Concat(RegEx):
    def __init__(self, a, b):
        super(Concat, self).__init__()
        self.a = a
        self.b = b
    
    def __iter__(self):
        return iter(('&', tuple(self.a), tuple(self.b)))
    
    def __str__(self):
        if self.a is not None and self.b is not None:
            return '(&, {}, {})'.format(self.a, self.b)
        elif self.a is not None:
            return self.a
        elif self.b is not None:
            return self.b
        else:
            return '\'\''

class Star(RegEx):
    def __init__(self, a):
        super(Star, self).__init__()
        self.a = a
    
    def __iter__(self):
        return iter(('*', tuple(self.a)))
    
    def __str__(self):
        return '(*, {})'.format(self.a)

class Primitive(RegEx):
    def __init__(self, c):
        super(Primitive, self).__init__()
        self.c = c
    
    def __iter__(self):
        return iter((self.c))
    
    def __str__(self):
        return repr(self.c)
    
    def __repr__(self):
        return 'Primitive({})'.format(self.c)

class REParser(object):
    def __init__(self, exp=None):
        self._input = exp

    def parse(self, tuples=False):
        tree = self._regex()
        
        if not tuples:
            return tree
        
        


    # parsing internals
    def _peek(self):
        return self._input[0]

    def _eat(self, c):
        if self._peek() == c:
            self._input = self._input[1:]
        else:
            raise RuntimeError('Expected: {}; got: {}'.format(c, self.peek()))
    
    def _next(self):
        c = self._peek()
        self._eat(c)
        return c
    
    def _more(self):
        return len(self._input) > 0


    # RE term types
    def _regex(self):
        """returns RegEx"""
        term = self._term()
        if self._more() and self._peek() == '|':
            self._eat('|')
            regex = self._regex()
            return Or(term, regex)
        else:
            return term

    def _term(self):
        """returns RegEx"""
        factor = None
        
        while self._more() and self._peek() not in (')', '|'):
            nextfactor = self._factor()
            if factor is None:
                factor = nextfactor
            else:
                factor = Concat(factor, nextfactor)
        
        return factor or RegEx()

    def _factor(self):
        """returns RegEx"""
        base = self._base()
        
        while self._more() and self._peek() == '*':
            self._eat('*')
            base = Star(base)
        
        return base

    def _base(self):
        """returns RegEx"""
        if self._peek() == '(':
            self._eat('(')
            r = self._regex()
            self._eat(')')
            return r
        elif self._peek() == '\\':
            self._eat('\\')
            esc = self._next()
            return Primitive(esc)
        else:
            return Primitive(self._next())

if __name__ == '__main__':
    parser = REParser('(ab)*|cd')
    print(parser.parse())