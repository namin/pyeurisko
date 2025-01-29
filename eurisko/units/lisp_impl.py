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
def repeat2(s, s2, f, registry):
    # Check compatibility
    if not (memb('structure', getattr(s, 'generalizations', [])) and
            memb('structure', getattr(s2, 'generalizations', [])) and
            memb('op', getattr(f, 'isa', [])) and
            len(getattr(f, 'domain', [])) == 3):
        return None
            
    # Check domain compatibility
    f_domains = getattr(f, 'domain', [])
    if not is_a_kind_of(s2, f_domains[1]):  # Second argument compatibility
        return None
        
    # Check third argument (element) compatibility
    if f_domains[2] != 'anything':
        typmem = getattr(s, 'each-element-is-a', None)
        if not (typmem and is_a_kind_of(typmem, f_domains[2])):
            return None
            
    # Check range compatibility with first argument 
    if not is_a_kind_of(f_domains[0], f_domains[0]):
        return None
                
    # Create new unit name
    new_name = f'repeat2-{f.name}-on-s-with-a-{s2.name}-as-param'
    new_unit = registry.create_unit(new_name)
    
    # Copy and modify isa
    new_isa = list(getattr(f, 'isa', []))
    new_isa = [('binary-op' if x == 'tertiary-op' else x) for x in new_isa]
    new_isa = [('binary-pred' if x == 'tertiary-pred' else x) for x in new_isa]
    new_unit.set_prop('isa', new_isa)
    
    # Set worth and properties
    new_unit.set_prop('worth', average_worths('repeat2', average_worths(f, average_worths(s, s2))))
    new_unit.set_prop('arity', 2)
    new_unit.set_prop('domain', [s.name, s2.name])
    new_unit.set_prop('range', list(getattr(f, 'range', [])))
    
    # Define algorithm that repeatedly applies f
    def repeat_alg(struct, param):
        if not struct:
            return None
        result = struct[0]
        for e in struct[1:]:
            result = run_alg(f.name, result, param, e)
        return result
    new_unit.set_prop('unitized-alg', repeat_alg)
    
    # Set administrative properties
    new_unit.set_prop('elim-slots', ['applics'])
    new_unit.set_prop('creditors', ['repeat2'])
    
    return new_unit

def list_delete_1(x, s):
    """Delete the first occurrence of x from s.
    
    In LISP:
    (lambda (x s) (cond ((null s) ())
                         ((equal x (car s)) (cdr s))
                         (t (cons (car s)
                                 (run-alg 'list-delete-1 x (cdr s))))))
    """
    if not s:
        return []
    if equals(x, s[0]):
        return s[1:]
    return [s[0]] + list_delete_1(x, s[1:])

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

def repeat2(s, s2, f, registry):
    # Check compatibility
    if not (memb('structure', getattr(s, 'generalizations', [])) and
            memb('structure', getattr(s2, 'generalizations', [])) and
            memb('op', getattr(f, 'isa', [])) and
            len(getattr(f, 'domain', [])) == 3):
        return None
            
    # Check domain compatibility 
    f_domains = getattr(f, 'domain', [])
    if not is_a_kind_of(s2, f_domains[1]):  # Second argument compatibility
        return None

    if f_domains[2] != 'anything':  # Third argument compatibility
        typmem = getattr(s, 'each-element-is-a', None)
        if not (typmem and is_a_kind_of(typmem, f_domains[2])):
            return None

    # Check first argument compatibility
    if not is_a_kind_of(car(getattr(f, 'range', [])), f_domains[0]):
        return None
                
    # Create new unit name
    new_name = f'repeat2-{f.name}-on-{s.name}-with-a-{s2.name}-as-param'
    new_unit = registry.create_unit(new_name)
        
    # Copy and modify properties
    isa = list(getattr(f, 'isa', []))
    isa = [('binary-op' if x == 'tertiary-op' else
            'binary-pred' if x == 'tertiary-pred' else x)
           for x in isa]
    new_unit.set_prop('isa', isa)
    
    new_unit.set_prop('worth', average_worths('repeat2', f, s, s2))
    new_unit.set_prop('arity', 2)
    new_unit.set_prop('domain', [s.name, s2.name])
    new_unit.set_prop('range', list(getattr(f, 'range', [])))

    # Define the algorithm that accumulates over elements
    def repeat2_alg(struct, param):
        if not isinstance(struct, (list, tuple)):
            return 'failed'
        val = struct[0]
        for e in struct[1:]:
            val = run_alg(f.name, val, param, e)
        return val
    new_unit.set_prop('unitized-alg', repeat2_alg)
        
    # Set administrative properties
    new_unit.set_prop('elim-slots', ['applics'])
    new_unit.set_prop('creditors', ['repeat2'])
        
    return new_unit

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

def bag_difference_recursive(s1, s2):
    """Recursive implementation of bag difference."""
    if not s1:
        return []
    if member(s1[0], s2):
        # Remove one occurrence from s2
        return bag_difference_recursive(s1[1:], list_delete_1(s1[0], s2))
    return [s1[0]] + bag_difference_recursive(s1[1:], s2)

def o_set_difference_recursive(s1, s2):
    """Recursive implementation of ordered set difference."""
    if not s1:
        return []
    if member(s1[0], s2):
        return o_set_difference_recursive(s1[1:], s2)
    return [s1[0]] + o_set_difference_recursive(s1[1:], s2)

def o_set_union_recursive(s1, s2):
    """Recursive implementation of ordered set union."""
    if not s1:
        return s2
    if member(s1[0], s2):
        return o_set_union_recursive(s1[1:], s2)
    return [s1[0]] + o_set_union_recursive(s1[1:], s2)

def bag_equal_recursive(s1, s2):
    """Recursive implementation of bag equality."""
    if not s1 and not s2:
        return True
    if not s1 or not s2:
        return False
    if not member(s1[0], s2):
        return False
    return bag_equal_recursive(s1[1:], list_delete_1(s1[0], s2))

def list_equal_recursive(s1, s2):
    """Recursive implementation of list equality."""
    if not s1 and not s2:
        return True
    if not s1 or not s2:
        return False
    return equals(s1[0], s2[0]) and list_equal_recursive(s1[1:], s2[1:])

def o_set_equal_recursive(s1, s2):
    """Recursive implementation of ordered set equality."""
    if not s1 and not s2:
        return True
    if not s1 or not s2:
        return False
    return equals(s1[0], s2[0]) and o_set_equal_recursive(s1[1:], s2[1:])

def restrict(f, registry):
    """Restrict an operation to use a more specific type for one of its arguments."""
    # Select random argument with specializations
    garg = random_choose(subset(getattr(f, 'domain', []), lambda x: getattr(registry.get_unit(x), 'specializations', [])))
    if not garg:
        return 'failed'

    # Get random specialization and substitute it
    spec = random_choose(getattr(registry.get_unit(garg), 'specializations', []))
    if not spec:
        return 'failed'

    newdom = random_subst(spec, garg, getattr(f, 'domain', []))
    if newdom == getattr(f, 'domain', []):
        return 'failed'

    # Create new restricted operation
    new_name = f'restrict-{f.name}'
    new_unit = registry.create_unit(new_name)

    # Copy and set properties
    new_unit.set_prop('isa', list(getattr(f, 'isa', [])))
    new_unit.set_prop('worth', average_worths('restrict', f))
    new_unit.set_prop('arity', getattr(f, 'arity', 0))
    new_unit.set_prop('domain', newdom)
    new_unit.set_prop('range', list(getattr(f, 'range', [])))

    # Define algorithm that just calls original operation
    def restricted_alg(*args):
        return run_alg(f.name, *args)
    new_unit.set_prop('unitized-alg', restricted_alg)

    # Set administrative properties
    new_unit.set_prop('extensions', [f.name])
    new_unit.set_prop('elim-slots', ['applics'])
    new_unit.set_prop('creditors', ['restrict'])

    return new_unit

def average_worths(*args):
    """Calculate average worth of units and values.
    
    Args:
        *args: Units and values to average
        
    Returns:
        Average worth value
    """
    total = 0
    count = 0
    for arg in args:
        if hasattr(arg, 'worth'):
            total += arg.worth
            count += 1
        elif isinstance(arg, (int, float, str)):
            total += 500  # Default worth
            count += 1
        elif isinstance(arg, list):
            for x in arg:
                if hasattr(x, 'worth'):
                    total += x.worth
                    count += 1
    return total // count if count > 0 else 500

def mult_ele_struc_delete_1(x, s):
    """Delete the first occurrence of x from multiple-element structure s.
    
    Similar to list-delete-1 but generalized for any multiple element structure.
    
    Args:
        x: Element to delete
        s: Multiple element structure
    
    Returns:
        Structure with first occurrence of x removed
    """
    if not s:
        return []
    if equals(x, car(s)):
        return cdr(s)
    return cons(car(s), mult_ele_struc_delete_1(x, cdr(s)))

def bag_delete_1(x, s):
    """Delete the first occurrence of x from bag s.
    
    Same as mult_ele_struc_delete_1 since bags have same representation.
    
    Args:
        x: Element to delete
        s: Bag structure
    
    Returns:
        Bag with first occurrence of x removed
    """
    if not s:
        return []
    if equals(x, car(s)):
        return cdr(s)
    return cons(car(s), bag_delete_1(x, cdr(s)))

def bag_delete(x, s):
    """Delete all occurrences of x from bag s.
    
    Args:
        x: Element to delete
        s: Bag structure
        
    Returns:
        Bag with all occurrences of x removed
    """
    if not s:
        return []
    if equals(x, car(s)):
        return bag_delete(x, cdr(s))
    return cons(car(s), bag_delete(x, cdr(s)))

def recursive_list_defn(s):
    """Recursive definition for list type.
    
    Args:
        s: Structure to check
        
    Returns:
        True if s is a valid list (empty or cons cell), False otherwise
    """
    if not isinstance(s, (list, tuple)):
        return s == []
    return recursive_list_defn(cdr(s))

def compose(f, g, registry):
    """Compose two operations f and g.
    
    Creates a new operation that applies g to the result of applying f to arguments.
    
    Args:
        f: First operation 
        g: Second operation
        registry: Unit registry for creating new unit
    
    Returns:
        New composed operation unit or None if composition not possible
    """
    f_range = getattr(f, 'range', [])
    g_domain = getattr(g, 'domain', [])
    
    if not (f_range and g_domain and is_a_kind_of(f_range[0], g_domain[0])):
        return None
        
    # Create new composed operation
    new_name = f'{g.name}-o-{f.name}'
    new_unit = registry.create_unit(new_name)
    
    # Set properties
    new_unit.set_prop('isa', list(set_difference(
        getattr(g, 'isa', []), 
        getattr(registry.get_unit('op-cat-by-nargs'), 'examples', [])
    )))
    new_unit.set_prop('worth', average_worths('compose', f, g))
    
    # Set up arguments
    f_args = zip(getattr(f, 'domain', []), 
                ['u', 'v', 'w', 'x', 'y', 'z', 'z2', 'z3', 'z4', 'z5'])
    g_args = zip(getattr(g, 'domain', [])[1:],
                ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'])
    
    f_args = list(f_args)
    g_args = list(g_args)
    
    new_unit.set_prop('arity', len(f_args) + len(g_args))
    new_unit.set_prop('domain', 
        [a[0] for a in f_args] + [a[0] for a in g_args])
    new_unit.set_prop('range', list(getattr(g, 'range', [])))
    
    # Define composition algorithm
    def composed_alg(*args):
        f_args_count = len(f_args)
        f_result = run_alg(f.name, *args[:f_args_count])
        return run_alg(g.name, f_result, *args[f_args_count:])
    new_unit.set_prop('unitized-alg', composed_alg)
    
    # Set administrative properties
    new_unit.set_prop('elim-slots', ['applics'])
    new_unit.set_prop('creditors', ['compose'])
    
    # Update ISA based on actual properties
    op_cats = getattr(registry.get_unit('op-cat-by-nargs'), 'examples', [])
    matching_cats = [pc for pc in op_cats if run_defn(pc, new_unit)]
    new_unit.set_prop('isa', list(set(new_unit.get_prop('isa', [])) | set(matching_cats)))
        
    return new_unit
    
def divisors_of(n):
    """Find all divisors of a number n.
    
    Args:
        n: Number to find divisors for
        
    Returns:
        Sorted list of all divisors of n
    """
    # Edge cases
    if not isinstance(n, int) or n < 1:
        return []
        
    # Find divisors up to square root    
    divisors = []
    i = 1
    while i*i <= n:
        if n % i == 0:
            divisors.append(i)
            if i*i != n: # Don't count square root twice
                divisors.append(n//i)
        i += 1
            
    return sorted(divisors)

def unitized_even_defn(n):
    """Definition for even number using divide by 2.
    
    Args:
        n: Number to test
        
    Returns:
        True if n is evenly divisible by 2, False otherwise
    """
    return divides(2, n)

def unitized_multiply_alg(x, y):
    """Multiply x and y using repeated addition.
    
    Args:
        x: First factor
        y: Second factor
        
    Returns:
        Product x*y
    """
    if x == 0:
        return 0
    if x == 1:
        return y
    return run_alg('add', y, run_alg('multiply', x-1, y))

def unitized_odd_defn(n):
    """Definition for odd number using divide by 2.
    
    Args:
        n: Number to test
        
    Returns:
        True if n is not evenly divisible by 2, False otherwise
    """
    return not divides(2, n)

def unitized_perfect_defn(n):
    """Definition for perfect number using divisors.
    
    Args:
        n: Number to test
        
    Returns:
        True if sum of proper divisors equals n, False otherwise  
    """
    return run_alg('double', n) == sum(divisors_of(n))

def recursive_set_defn(s):
    """Recursive definition for set type.
    
    Args:
        s: Structure to test
        
    Returns:
        True if s is a valid set (no duplicates), False otherwise
    """
    if not isinstance(s, (list, tuple)):
        return s == []
    return not member(car(s), cdr(s)) and recursive_set_defn(cdr(s))

def recursive_bag_equal(s1, s2):
    """Recursive definition for bag equality.
    
    Args:
        s1: First bag
        s2: Second bag
        
    Returns:
        True if bags contain same elements with same multiplicity
    """
    if not s1 and not s2:
        return True
    if not s1 or not s2:
        return False
    return memb(s1[0], s2) and bag_equal_recursive(s1[1:], list_delete_1(s1[0], s2))

def recursive_set_equal(s1, s2):
    """Recursive definition for set equality using subset.
    
    Args:
        s1: First set
        s2: Second set
        
    Returns:
        True if sets contain same elements
    """
    return is_subset_of(s1, s2) and is_subset_of(s2, s1)

def unitized_set_equal(s1, s2):
    """Definition for set equality using subset.
    
    Args:
        s1: First set 
        s2: Second set
        
    Returns:
        True if sets contain same elements
    """
    return run_alg('subsetp', s1, s2) and run_alg('subsetp', s2, s1)
