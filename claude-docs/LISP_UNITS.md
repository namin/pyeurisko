# Porting LISP Units to Python

## File Structure

The LISP unit functionality is spread across several files in the `/projects/code/pyeurisko/eurisko/units/` directory:

### Core Files
- `lisp_units.py`: Contains the main unit definitions and TODO implementations that need to be ported. This is where most of the work happens.
- `lisp_impl.py`: Contains core LISP functionality implemented in Python (cons, car, cdr, etc.). This provides the foundation for implementing the unit operations.

### Workflow
1. Ensure core LISP operations are implemented in `lisp_impl.py`
2. Port TODO implementations in `lisp_units.py` using these core operations
3. Add any necessary utility functions to `lisp_impl.py` as needed
4. Test implementations through running `python -m main.eurisko` without fault.

## Types of TODOs

There are three main categories of TODOs in the LISP unit code:

1. Simple Recursive Algorithms
2. Complex Recursive Algorithms 
3. Unit Manipulation Operations

### Simple Recursive Algorithms

These are straightforward translations of LISP list operations. Example from list-union:

```lisp
(lambda (s1 s2) 
  (cond ((null s1) s2)
        (t (cons (car s1) 
                (run-alg 'list-union (cdr s1) s2)))))
```

Porting guidelines:
- Translate LISP conditionals (`cond`) to Python `if/else`
- Replace `car`/`cdr` with Python list indexing/slicing (`[0]`, `[1:]`)
- Keep recursion structure but use Python list concatenation (`+`)
- Maintain function signatures as `(s1, s2)` pairs

Python equivalent:
```python
lambda s1, s2: s2 if not s1 else [s1[0]] + run_alg('list-union', s1[1:], s2)
```

### Complex Recursive Algorithms

These involve multiple conditions and nested operations. Example from set-difference:

```lisp
(lambda (s1 s2) 
  (cond ((null s1) ())
        ((member (car s1) s2) 
         (run-alg 'set-difference (cdr s1) s2))
        (t (cons (car s1) 
                (run-alg 'set-difference (cdr s1) s2)))))
```

Porting guidelines:
- Break down nested conditions into clear Python logic
- Use helper functions from lisp_impl.py (e.g., `member()`)
- Test edge cases like empty lists carefully
- Consider replacing deep recursion with iteration for performance

Python equivalent:
```python
lambda s1, s2: (
    [] if not s1 else
    (run_alg('set-difference', s1[1:], s2) 
     if member(s1[0], s2) 
     else [s1[0]] + run_alg('set-difference', s1[1:], s2))
)
```

### Unit Manipulation Operations

These are the most complex TODOs, involving unit creation and property manipulation. Example from parallel-replace:

```lisp
(lambda (s f) 
  (cond 
    ((and (memb 'structure (generalizations s))
          (memb 'op (isa f))
          (eq 1 (length (domain f)))
          (or (eq 'anything (car (domain f)))
              (let ((typmem (each-element-is-a s)))
                (and typmem (is-a-kind-of typmem (car (domain f)))))))
     (let ((nam (create-unit (pack* 'perform- f '-on- s 's))))
       (put nam 'isa (copy (isa f)))
       (put nam 'worth (average-worths 'parallel-replace 
                                     (average-worths f s)))
       ...))
    (t 'failed)))
```

Porting guidelines:
- Break down into clear phases:
  1. Input validation and type checking
  2. Unit creation
  3. Property setup
  4. Algorithm definition
  5. Relationship establishment
- Use helper functions to encapsulate common patterns
- Maintain consistent error handling
- Document complex logic in comments
- Test unit creation and property inheritance thoroughly

Python equivalent:
```python
def parallel_replace(s, f, registry):
    # Phase 1: Validation
    if not (memb('structure', getattr(s, 'generalizations', [])) and
            memb('op', getattr(f, 'isa', [])) and
            len(getattr(f, 'domain', [])) == 1):
        return None
        
    # Phase 2: Domain compatibility
    f_domain = getattr(f, 'domain', [])[0]
    if f_domain != 'anything':
        typmem = getattr(s, 'each-element-is-a', None)
        if not (typmem and is_a_kind_of(typmem, f_domain)):
            return None
    
    # Phase 3: Unit creation
    new_name = f'perform-{f.name}-on-{s.name}s'
    new_unit = registry.create_unit(new_name)
    
    # Phase 4: Property setup
    new_unit.set_prop('isa', list(getattr(f, 'isa', [])))
    new_unit.set_prop('worth', (getattr(f, 'worth', 500) + 
                               getattr(s, 'worth', 500)) // 2)
    new_unit.set_prop('arity', 1)
    new_unit.set_prop('domain', [s.name])
    
    # Phase 5: Algorithm definition
    def apply_to_all(struct):
        return [run_alg(f.name, e) for e in struct]
    new_unit.set_prop('unitized-alg', apply_to_all)
    
    return new_unit
```

## Common Patterns and Utilities

### Property Access
- Use `getattr(obj, 'prop', default)` for safe property access
- Always provide defaults for missing properties
- Consider wrapping common property patterns in helper functions

### Unit Creation
- Use registry's create_unit method
- Copy required properties from parent units
- Set up proper relationships
- Define algorithms last after all properties are set

### Algorithm Definition
- Keep algorithms as pure functions when possible
- Use closure scope for accessing unit properties
- Document complex algorithms with examples
- Consider performance implications of recursion

## Testing Strategy

1. Start with simple recursive algorithms
2. Test edge cases (empty lists, invalid inputs)
3. Verify property inheritance in unit creation
4. Check relationship establishment
5. Test algorithm execution
6. Verify complex operations end-to-end

## Common Pitfalls

1. Missing property defaults leading to AttributeErrors
2. Improper list operation translations
3. Deep recursion performance issues
4. Incomplete property copying
5. Missing relationship establishment
6. Incorrect type checking logic

## Future Improvements

1. Consider replacing deep recursion with iteration
2. Add better error handling and logging
3. Create helper functions for common patterns
4. Add property validation
5. Improve performance of frequently used operations
6. Add more comprehensive testing
