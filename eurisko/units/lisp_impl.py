class DataType:
    """Data type definitions."""
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return f"DataType({self.name})"

# Define the core data types needed for the lisp unit system
# Core data types
UNIT = DataType("unit")  # For entities/concepts
NUMBER = DataType("number")  # For numerical values
NEXT = DataType("next")  # For next action in sequence
LISP_PRED = DataType("lisp-pred")  # For predicates  
LISP_FN = DataType("lisp-fn")  # For generic functions
STRING = DataType("string")  # For text values
BIT = DataType("bit")  # For boolean values
IO_PAIR = DataType("io-pair")  # For input/output pairs

def unit_type(x):
    """Data type check for units."""
    return isinstance(x, str) or x is None

class LispFunction:
    """Wrapper for Lisp function implementation in Python."""
    def __init__(self, fn, name=None):
        self.fn = fn
        self.name = name or fn.__name__
        
    def __call__(self, *args):
        return self.fn(*args)

def cons(x, y=None):
    """Basic cons cell implementation."""
    if y is None:
        return [x]
    if isinstance(y, list):
        return [x] + y
    return [x, y]

def memb(x, s):
    """Member predicate - checks if x is in s."""
    if not s or not isinstance(s, (list, tuple)):
        return False
    return x in s

def member(x, s):
    """Like memb but using equal for comparison."""
    if not s or not isinstance(s, (list, tuple)):
        return False
    return any(x == item for item in s)

def car(x):
    """Return first element of list."""
    if not isinstance(x, (list, tuple)) or not x:
        return None
    return x[0]

def cdr(x):
    """Return rest of list after first element."""
    if not isinstance(x, (list, tuple)) or len(x) <= 1:
        return []
    return x[1:]

def caddr(x):
    """Return third element of list."""
    if not isinstance(x, (list, tuple)) or len(x) < 3:
        return None 
    return x[2]

def cadr(x):
    """Return second element of list."""
    if not isinstance(x, (list, tuple)) or len(x) < 2:
        return None
    return x[1]

def not_(x):
    """Logical not."""
    return not x

def atom(x):
    """Test if x is an atom (non-list)."""
    return not isinstance(x, (list, tuple))

def null(x):
    """Test if x is null/empty."""
    if isinstance(x, (list, tuple)):
        return len(x) == 0
    return x is None

def consp(x):
    """Test if x is a cons cell (non-empty list)."""
    return isinstance(x, (list, tuple)) and len(x) > 0

def listp(x):
    """Test if x is a list."""
    return isinstance(x, (list, tuple))

def set_difference(s1, s2):
    """Return elements in s1 that are not in s2."""
    if not isinstance(s1, (list, tuple)):
        return []
    if not isinstance(s2, (list, tuple)):
        return s1
    return [x for x in s1 if x not in s2]

def equal(x, y):
    """Structural equality test."""
    if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
        if len(x) != len(y):
            return False
        return all(equal(a, b) for a, b in zip(x, y))
    return x == y

def append(*lists):
    """Append multiple lists together."""
    result = []
    for lst in lists:
        if isinstance(lst, (list, tuple)):
            result.extend(lst)
    return result

def length(x):
    """Return length of list or 0 for non-lists."""
    if isinstance(x, (list, tuple)):
        return len(x)
    return 0

def set_union(s1, s2):
    """Return union of two sets (lists with unique elements)."""
    if not isinstance(s1, (list, tuple)):
        return s2
    if not isinstance(s2, (list, tuple)):
        return s1
    result = list(s1)
    for x in s2:
        if x not in result:
            result.append(x)
    return result

def set_intersect(s1, s2):
    """Return intersection of two sets."""
    if not isinstance(s1, (list, tuple)) or not isinstance(s2, (list, tuple)):
        return []
    return [x for x in s1 if x in s2]

def no_repeats_in(s):
    """Check if list has no repeated elements."""
    if not isinstance(s, (list, tuple)):
        return True
    seen = set()
    for x in s:
        if x in seen:
            return False
        seen.add(x)
    return True

def repeats_in(s):
    """Check if list has any repeated elements."""
    return not no_repeats_in(s)

def remove_(x, s):
    """Remove all occurrences of x from s."""
    if not isinstance(s, (list, tuple)):
        return []
    return [y for y in s if y != x]

def best_choose(s):
    """Choose best element from set based on worth."""
    if not isinstance(s, (list, tuple)) or not s:
        return None
    return max(s, key=lambda x: getattr(x, 'worth', 0) if hasattr(x, 'worth') else 0)

def best_subset(s):
    """Choose best subset from set based on worth."""
    if not isinstance(s, (list, tuple)):
        return []
    return sorted(s, key=lambda x: getattr(x, 'worth', 0) if hasattr(x, 'worth') else 0, reverse=True)[:len(s)//2]

def good_choose(s):
    """Choose good element from set."""
    return best_choose(s)  # Simplified implementation

def good_subset(s):
    """Choose good subset from set."""
    return best_subset(s)  # Simplified implementation

def equals(x, y):
    """Structural equality test for general values."""
    if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
        if len(x) != len(y):
            return False
        return all(equals(a, b) for a, b in zip(x, y))
    return x == y

def equals_num(x, y):
    """Numerical equality test."""
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
        return False
    return x == y

def greater(x, y):
    """Greater than test for numbers."""
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
        return False
    return x > y

def greater_equal(x, y):
    """Greater than or equal test for numbers."""
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
        return False
    return x >= y

def less(x, y):
    """Less than test for numbers."""
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
        return False
    return x < y

def less_equal(x, y):
    """Less than or equal test for numbers."""
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
        return False
    return x <= y

def eq(x, y):
    """Simple equality test using Python's ==."""
    return x == y

def fixp(n):
    """Test if n is a fixed-point number (integer)."""
    return isinstance(n, int)

def divides(x, n):
    """Test if x divides n evenly."""
    if not (isinstance(x, int) and isinstance(n, int)):
        return False
    return x != 0 and n % x == 0

def last(s):
    """Return last element and rest of list."""
    if not isinstance(s, (list, tuple)) or not s:
        return None, []
    return s[-1], s[:-1]

def random_choose(s):
    """Choose random element from set."""
    if not isinstance(s, (list, tuple)) or not s:
        return None
    import random
    return random.choice(s)

def random_subset(s):
    """Choose random subset from set."""
    if not isinstance(s, (list, tuple)):
        return []
    import random
    size = random.randint(0, len(s))
    return random.sample(s, size)

def random_pair(s, pred):
    """Choose random pair of elements from s satisfying pred."""
    if not isinstance(s, (list, tuple)) or len(s) < 2:
        return None
    import random
    for _ in range(100):  # Try 100 times to find valid pair
        i = random.randint(0, len(s)-1)
        j = random.randint(0, len(s)-1)
        if i != j and (pred is None or pred(s[i], s[j])):
            return [i, j]
    return None

def is_subset_of(s1, s2):
    """Test if s1 is a subset of s2."""
    if not isinstance(s1, (list, tuple)) or not isinstance(s2, (list, tuple)):
        return False
    return all(x in s2 for x in s1)

def run_defn(type_name, value):
    """Apply type definition to value."""
    # This is a simplified implementation that trusts the type_name
    if type_name == 'structure':
        return isinstance(value, (list, tuple))
    elif type_name == 'set':
        return isinstance(value, (list, tuple)) and len(set(value)) == len(value)
    return True

def is_a_kind_of(x, y):
    """Test if x is a kind of y."""
    # Simplified implementation
    return True

def parallel_join(s, f, registry):
    # Check compatibility
    if not (memb('structure', getattr(s, 'generalizations', [])) and
            memb('op', getattr(f, 'isa', [])) and
            len(getattr(f, 'domain', [])) == 1):
        return None
            
    # Check domain compatibility
    f_domain = getattr(f, 'domain', [])[0]
    if f_domain != 'anything':
        typmem = getattr(s, 'each-element-is-a', None)
        if not (typmem and is_a_kind_of(typmem, f_domain)):
            return None

    # Additional check for range compatibility 
    f_range = getattr(f, 'range', [])[0] if getattr(f, 'range', []) else None
    if not (f_range and is_a_kind_of(f_range, 'structure')):
        return None
                    
    # Create new unit name
    new_name = f'join-{f.name}-on-{s.name}s'
    new_unit = registry.create_unit(new_name)
            
    # Copy properties
    new_unit.set_prop('isa', list(getattr(f, 'isa', [])))
    new_unit.set_prop('worth', (getattr(f, 'worth', 500) + getattr(s, 'worth', 500)) // 2)
    new_unit.set_prop('arity', 1)
    new_unit.set_prop('domain', [s.name])
    new_unit.set_prop('range', [f_range])
            
    # Define the algorithm that maps and appends f over elements
    def mapappend(struct):
        results = []
        for e in struct:
            result = run_alg(f.name, e)
            if isinstance(result, list):
                results.extend(result)
            else:
                results.append(result)
        return results
    new_unit.set_prop('unitized-alg', mapappend)
            
    # Set administrative properties
    new_unit.set_prop('elim-slots', ['applics'])
    new_unit.set_prop('creditors', ['parallel-join'])
            
    return new_unit

def parallel_join_2(s, s2, f, registry):
    # Check compatibility
    if not (memb('structure', getattr(s, 'generalizations', [])) and
            memb('structure', getattr(s2, 'generalizations', [])) and
            memb('op', getattr(f, 'isa', [])) and
            len(getattr(f, 'domain', [])) == 2):
        return None
            
    # Check domain compatibility
    f_domains = getattr(f, 'domain', [])
    if not is_a_kind_of(s2, f_domains[1]):  # Second argument compatibility
        return None
        
    if f_domains[0] != 'anything':  # First argument elements compatibility
        typmem = getattr(s, 'each-element-is-a', None)
        if not (typmem and is_a_kind_of(typmem, f_domains[0])):
            return None

    # Additional check for range compatibility 
    f_range = getattr(f, 'range', [])[0] if getattr(f, 'range', []) else None
    if not (f_range and is_a_kind_of(f_range, 'structure')):
        return None
                
    # Create new unit name
    new_name = f'join-{f.name}-on-{s.name}s-with-a-{s2.name}-as-param'
    new_unit = registry.create_unit(new_name)
        
    # Copy properties
    new_unit.set_prop('isa', list(getattr(f, 'isa', [])))
    new_unit.set_prop('worth', average_worths(f, s, s2))
    new_unit.set_prop('arity', 2)
    new_unit.set_prop('domain', [s.name, s2.name])
    new_unit.set_prop('range', [f_range])

    def map_and_append(struct, param):
        return mapappend(f, struct, param)
    new_unit.set_prop('unitized-alg', map_and_append)
        
    # Set administrative properties
    new_unit.set_prop('elim-slots', ['applics'])
    new_unit.set_prop('creditors', ['parallel-join-2'])
        
    return new_unit

def parallel_replace_2(s, s2, f, registry):
    # Check compatibility
    if not (memb('structure', getattr(s, 'generalizations', [])) and
            memb('structure', getattr(s2, 'generalizations', [])) and
            memb('op', getattr(f, 'isa', [])) and
            len(getattr(f, 'domain', [])) == 2):
        return None

    # Check domain compatibility
    f_domains = getattr(f, 'domain', [])
    if not is_a_kind_of(s2, f_domains[1]):  # Second argument compatibility
        return None
        
    if f_domains[0] != 'anything':  # First argument elements compatibility
        typmem = getattr(s, 'each-element-is-a', None)
        if not (typmem and is_a_kind_of(typmem, f_domains[0])):
            return None

    # Create new unit name
    new_name = f'perform-{f.name}-on-{s.name}s-with-a-{s2.name}-as-param'
    new_unit = registry.create_unit(new_name)
            
    # Copy properties
    new_unit.set_prop('isa', list(getattr(f, 'isa', [])))
    new_unit.set_prop('worth', average_worths(f, s, s2))
    new_unit.set_prop('arity', 2)
    new_unit.set_prop('domain', [s.name, s2.name])

    # Set range based on input structure
    f_range = getattr(f, 'range', [])[0] if getattr(f, 'range', []) else None
    if f_range:
        new_unit.set_prop('range', [f'{s.name}-of-{f_range}s'])
                
    # Define the algorithm that maps f over elements
    def map_and_transform(struct, param):
        return [run_alg(f.name, e, param) for e in struct]
    new_unit.set_prop('unitized-alg', map_and_transform)
            
    # Set administrative properties
    new_unit.set_prop('elim-slots', ['applics'])
    new_unit.set_prop('creditors', ['parallel-replace-2'])
            
    return new_unit
        
# Define the algorithm that maps and appends f over elements
def mapappend(f, struct, param=None):
    results = []
    for e in struct:
        if param is None:
            result = run_alg(f.name, e)
        else:
            result = run_alg(f.name, e, param)
        if isinstance(result, list):
            results.extend(result)
        else:
            results.append(result)
    return results

def average_worths(*units):
    """Calculate average worth of units."""
    worths = [getattr(u, 'worth', 500) for u in units]
    return sum(worths) // len(worths)

def random_subst(new, old, lst):
    """Randomly substitute some occurrences of old with new in lst."""
    import random
    if not isinstance(lst, list):
        return lst
    result = list(lst)
    for i, x in enumerate(result):
        if x == old and random.random() < 0.5:
            result[i] = new
    return result

def subset(s, pred):
    """Return subset of elements from s that satisfy pred."""
    if not isinstance(s, (list, tuple)):
        return []
    return [x for x in s if pred(x)]

def coalesce(f, registry):
    # Get random compatible pair of arguments
    coargs = random_pair(getattr(f, 'domain', []), is_a_kind_of)
    if not coargs:
        return None
        
    # Create new unit
    new_name = f'coa-{f.name}'
    new_unit = registry.create_unit(new_name)
    
    # Set isa excluding op categories
    new_unit.set_prop('isa', list(set_difference(
        getattr(f, 'isa', []), 
        getattr(registry.get_unit('op-cat-by-nargs'), 'examples', [])
    )))
    
    # Set worth and arity
    new_unit.set_prop('worth', average_worths('coalesce', f))
    new_unit.set_prop('arity', getattr(f, 'arity', 1) - 1)
    
    # Set up argument names and domain
    arg_names = ['u', 'v', 'w', 'x', 'y', 'z', 'z2', 'z3', 'z4', 'z5']
    fargs = list(zip(getattr(f, 'domain', []), arg_names))
    newargs = fargs.copy()
    
    # Modify domain and arguments
    ca1, ca2 = coargs
    newargs[ca2] = (newargs[ca1][0], newargs[ca2][1])
    
    if ca2 <= 1:
        newargs.pop(0)
    else:
        newargs = newargs[:ca2] + newargs[ca2+1:]
        
    new_unit.set_prop('domain', [a[0] for a in newargs])
    new_unit.set_prop('range', list(getattr(f, 'range', [])))
    
    # Set up the algorithm
    def coalesced_alg(*args):
        newargs = list(args)
        newargs.insert(ca1, args[ca2])
        return run_alg(f.name, *newargs)
    new_unit.set_prop('unitized-alg', coalesced_alg)
    
    # Set administrative properties  
    new_unit.set_prop('elim-slots', ['applics'])
    new_unit.set_prop('creditors', ['coalesce'])
    
    # Update ISA based on checking op categories
    op_cats = getattr(registry.get_unit('op-cat-by-nargs'), 'examples', [])
    matchingcats = [pc for pc in op_cats if run_defn(pc, new_unit)]
    new_unit.set_prop('isa', 
        list(set(new_unit.get_prop('isa', [])) | set(matchingcats))
    )
        
    return new_unit

