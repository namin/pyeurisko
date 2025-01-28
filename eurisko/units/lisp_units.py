"""Generated unit initializations from LISP definitions."""

from typing import Dict, Any
from ..units import Unit, UnitRegistry
import logging
def TODO(original_lisp):
    """Placeholder for unimplemented LISP functionality.
    Args:
        original_lisp: The original LISP code to be implemented
    Returns:
        A function that logs a warning and returns None
    """
    def todo_func(*args, **kwargs):
        logging.warning(f'Called unimplemented function. Original LISP: {original_lisp}')
        return None
    return todo_func
from .lisp_impl import *
def Quoted(x): return x # hack
def Symbol(x): return x # hack

def initialize_lisp_units(registry: UnitRegistry) -> None:
    """Initialize lisp units."""

    # int-applics
    unit = registry.create_unit('int-applics')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('less-interesting', ['applics'])
    unit.set_prop('super-slots', ['applics'])
    unit.set_prop('worth', 500)

    # mult-ele-struc-insert
    unit = registry.create_unit('mult-ele-struc-insert')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'mult-ele-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', cons)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'mult-ele-struc-op', 'binary-op'])
    unit.set_prop('range', ['mult-ele-struc'])
    unit.set_prop('specializations', ['list-insert', 'bag-insert'])
    unit.set_prop('worth', 500)

    # rarity
    unit = registry.create_unit('rarity')
    unit.set_prop('data-type', NUMBER)
    unit.set_prop('dont-copy', True)
    unit.set_prop('format', ['frequency-true', 'number-t', 'number-f'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 500)

    # why-int
    unit = registry.create_unit('why-int')
    unit.set_prop('data-type', NEXT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # is-a-int
    unit = registry.create_unit('is-a-int')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['int-examples'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # int-examples
    unit = registry.create_unit('int-examples')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['is-a-int'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('less-interesting', ['examples'])
    unit.set_prop('super-slots', ['examples'])
    unit.set_prop('worth', 500)

    # less-interesting
    unit = registry.create_unit('less-interesting')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('inverse', ['more-interesting'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # more-interesting
    unit = registry.create_unit('more-interesting')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('inverse', ['less-interesting'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # interestingness
    unit = registry.create_unit('interestingness')
    unit.set_prop('abbrev', ['What would make an instance of this unit interesting?'])
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('double-check', True)
    unit.set_prop('english', ['What features or properties would an example or applic of this unit possess which would make it unusually interesting?'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # restrictions
    unit = registry.create_unit('restrictions')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['extensions'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['specializations'])
    unit.set_prop('worth', 300)

    # extensions
    unit = registry.create_unit('extensions')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['restrictions'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['generalizations'])
    unit.set_prop('worth', 300)

    # op-cat-by-nargs
    unit = registry.create_unit('op-cat-by-nargs')
    unit.set_prop('examples', ['unary-pred', 'binary-pred', 'tertiary-pred', 'unary-op', 'binary-op', 'tertiary-op'])
    unit.set_prop('generalizations', ['category'])
    unit.set_prop('isa', ['category', 'anything', 'repr-concept'])
    unit.set_prop('specializations', ['pred-cat-by-nargs'])
    unit.set_prop('worth', 500)

    # pred-cat-by-nargs
    unit = registry.create_unit('pred-cat-by-nargs')
    unit.set_prop('examples', ['unary-pred', 'binary-pred', 'tertiary-pred'])
    unit.set_prop('generalizations', ['category', 'op-cat-by-nargs'])
    unit.set_prop('isa', ['category', 'anything', 'repr-concept'])
    unit.set_prop('worth', 500)

    # tertiary-pred
    unit = registry.create_unit('tertiary-pred')
    unit.set_prop('fast-defn', lambda f: memb('pred', getattr(f, 'isa', [])) and getattr(f, 'arity', 0) == 3)
    unit.set_prop('generalizations', ['tertiary-op', 'pred', 'op', 'anything'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category', 'pred-cat-by-nargs', 'op-cat-by-nargs'])
    unit.set_prop('lower-arity', ['binary-pred'])
    unit.set_prop('rarity', [0.1827957, 17, 76])
    unit.set_prop('worth', 500)

    # unary-pred
    unit = registry.create_unit('unary-pred')
    unit.set_prop('examples', ['always-t', 'always-nil', 'constant-unary-pred', 'undefined-pred', 'not'])
    unit.set_prop('fast-defn', lambda f: print(f'unary-pred called for {f} with result {r}') or r if (r := memb('pred', getattr(f, 'isa', [])) and getattr(f, 'arity', 0) == 1) else False)
    unit.set_prop('generalizations', ['unary-op', 'pred', 'op', 'anything'])
    unit.set_prop('higher-arity', ['binary-pred'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category', 'pred-cat-by-nargs', 'op-cat-by-nargs'])
    unit.set_prop('rarity', [0.1182796, 11, 82])
    unit.set_prop('worth', 500)

    # binary-pred
    unit = registry.create_unit('binary-pred')
    unit.set_prop('examples', ['equal', 'ieqp', 'eq', 'ileq', 'igeq', 'ilessp', 'igreaterp', 'and', 'or', 'the-second-of', 'the-first-of', 'struc-equal', 'set-equal', 'subsetp', 'constant-binary-pred', 'always-t-2', 'always-nil-2', 'o-set-equal', 'bag-equal', 'list-equal', 'member', 'memb', 'implies'])
    unit.set_prop('fast-defn', lambda f: memb('pred', getattr(f, 'isa', [])) and getattr(f, 'arity', 0) == 2)
    unit.set_prop('generalizations', ['binary-op', 'pred', 'op', 'anything'])
    unit.set_prop('higher-arity', ['tertiary-pred'])
    unit.set_prop('int-examples', ['ieqp', 'eq', 'struc-equal', 'set-equal', 'o-set-equal', 'bag-equal', 'list-equal', 'memb', 'member'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category', 'pred-cat-by-nargs', 'op-cat-by-nargs'])
    unit.set_prop('lower-arity', ['unary-pred'])
    unit.set_prop('rarity', [0.07526882, 7, 86])
    unit.set_prop('worth', 500)

    # higher-arity
    unit = registry.create_unit('higher-arity')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('inverse', ['lower-arity'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # lower-arity
    unit = registry.create_unit('lower-arity')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('inverse', ['higher-arity'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # non-empty-struc
    unit = registry.create_unit('non-empty-struc')
    unit.set_prop('examples', [])
    unit.set_prop('fast-defn', consp)
    unit.set_prop('generalizations', ['structure', 'anything', 'set', 'list', 'bag', 'mult-ele-struc', 'o-set', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc', 'pair', 'o-pair'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('worth', 500)

    # empty-struc
    unit = registry.create_unit('empty-struc')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', null)
    unit.set_prop('generalizations', ['structure', 'anything', 'set', 'list', 'bag', 'mult-ele-struc', 'o-set', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('worth', 500)

    # set-of-sets
    unit = registry.create_unit('set-of-sets')
    unit.set_prop('each-element-is-a', UNIT)
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('generalizations', ['anything', 'structure-of-structures'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['relation'])
    unit.set_prop('unitized-defn', lambda s: run_defn('set', s) and all(run_defn('set', n) for n in s))
    unit.set_prop('worth', 500)

    # structure-of-structures
    unit = registry.create_unit('structure-of-structures')
    unit.set_prop('each-element-is-a', UNIT)
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['set-of-o-pairs', 'set-of-sets'])
    unit.set_prop('unitized-defn', lambda s: run_defn('structure', s) and all(run_defn('structure', n) for n in s))
    unit.set_prop('worth', 500)

    # truth-value
    unit = registry.create_unit('truth-value')
    unit.set_prop('examples', [True, []])
    unit.set_prop('fast-defn', lambda x: not x or x is True)
    unit.set_prop('generalizations', ['anything', 'atom'])
    unit.set_prop('isa', ['anything', 'category', 'math-obj'])
    unit.set_prop('worth', 500)

    # atom
    unit = registry.create_unit('atom')
    unit.set_prop('fast-defn', atom)
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('isa', ['anything', 'category', 'repr-concept'])
    unit.set_prop('specializations', ['truth-value'])
    unit.set_prop('worth', 500)

    # implies
    unit = registry.create_unit('implies')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: y if not x else True)
    unit.set_prop('isa', ['op', 'pred', 'math-op', 'math-pred', 'anything', 'binary-op', 'logic-op', 'binary-pred'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('unitized-alg', TODO("(lambda (x y) (run-alg 'or (run-alg 'not x) y))"))
    unit.set_prop('worth', 500)

    # not
    unit = registry.create_unit('not')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', not_)
    unit.set_prop('isa', ['op', 'pred', 'math-op', 'math-pred', 'anything', 'unary-op', 'logic-op', 'unary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('worth', 500)

    # logic-op
    unit = registry.create_unit('logic-op')
    unit.set_prop('abbrev', ['Logical operations'])
    unit.set_prop('examples', ['and', 'or', 'the-first-of', 'the-second-of', 'not', 'implies'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything', 'struc-op'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # relation
    unit = registry.create_unit('relation')
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('unitized-defn', lambda s: run_defn('set', s) and all(run_defn('o-pair', n) for n in s))
    unit.set_prop('worth', 500)

    # set-of-o-pairs
    unit = registry.create_unit('set-of-o-pairs')
    unit.set_prop('each-element-is-a', UNIT)
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('generalizations', ['anything', 'structure-of-structures'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['relation'])
    unit.set_prop('unitized-defn', lambda s: run_defn('set', s) and all(run_defn('o-pair', n) for n in s))
    unit.set_prop('worth', 500)

    # invert-op
    unit = registry.create_unit('invert-op')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['inverted-op'])
    unit.set_prop('worth', 100)

    # inverted-op
    unit = registry.create_unit('inverted-op')
    unit.set_prop('abbrev', ['Operations which were formed via InvertOp'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything'])
    unit.set_prop('is-range-of', ['invert-op'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # restrict
    unit = registry.create_unit('restrict')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', TODO("(lambda (f) (let* ((garg (random-choose (subset (domain f) \\#\\'specializations))) (newdom (random-subst (random-choose (specializations garg)) garg (domain f)))) (cond ((and garg newdom (not (equal newdom (domain f)))) (let ((nam (create-unit (pack* 'restrict- f)))) (put nam 'isa (copy (isa f))) (put nam 'worth (average-worths 'restrict f)) (put nam 'arity (arity f)) (let ((fargs (mapcar \\#\\'the-second-of (domain f) '(u v w x y z z2 z3 z4 z5)))) (put nam 'domain newdom) (put nam 'range (copy (range f))) (put nam 'unitized-alg (compile-report \\` (lambda \\,fargs (run-alg '\\,f \\,@fargs))))) (put nam 'extensions (list f)) (put nam 'elim-slots '(applics)) (put nam 'creditors '(restrict)) (add-inv nam) nam)) (t 'failed))))"))
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['op'])
    unit.set_prop('worth', 600)

    # identity-1
    unit = registry.create_unit('identity-1')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x: x)
    unit.set_prop('generalizations', ['proj1', 'proj2', 'proj-1-of-3', 'proj-2-of-3', 'proj-3-of-3'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # proj-3-of-3
    unit = registry.create_unit('proj-3-of-3')
    unit.set_prop('arity', 3)
    unit.set_prop('domain', ['anything', 'anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y, z: z)
    unit.set_prop('isa', ['math-concept', 'math-op', 'anything', 'tertiary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['identity-1'])
    unit.set_prop('worth', 500)

    # proj-2-of-3
    unit = registry.create_unit('proj-2-of-3')
    unit.set_prop('arity', 3)
    unit.set_prop('domain', ['anything', 'anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y, z: y)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'tertiary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['identity-1'])
    unit.set_prop('worth', 500)

    # proj-1-of-3
    unit = registry.create_unit('proj-1-of-3')
    unit.set_prop('arity', 3)
    unit.set_prop('domain', ['anything', 'anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y, z: x)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'tertiary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['identity-1'])
    unit.set_prop('worth', 500)

    # proj2
    unit = registry.create_unit('proj2')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applic'])
    unit.set_prop('fast-alg', lambda x, y: y)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'binary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['identity-1'])
    unit.set_prop('worth', 500)

    # proj1
    unit = registry.create_unit('proj1')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: x)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'binary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['identity-1'])
    unit.set_prop('worth', 500)

    # memb
    unit = registry.create_unit('memb')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'structure'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', memb)
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.1, 1, 9])
    unit.set_prop('recursive-alg', lambda x, s: None if not s else True if eq(x, s[0]) else run_alg('memb', x, s[1:]))
    unit.set_prop('worth', 500)

    # member
    unit = registry.create_unit('member')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'structure'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', member)
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'math-pred', 'pred', 'anything', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.1, 1, 9])
    unit.set_prop('recursive-alg', lambda x, s: None if not s else True if equals(x, s[0]) else run_alg('member', x, s[1:]))
    unit.set_prop('worth', 500)

    # all-but-last
    unit = registry.create_unit('all-but-last')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda s: s[:-1])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # last-ele
    unit = registry.create_unit('last-ele')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda s: last(s)[0])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # all-but-third
    unit = registry.create_unit('all-but-third')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda s: [s[0], s[1]] + s[3:])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # all-but-second
    unit = registry.create_unit('all-but-second')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda s: [s[0]] + s[2:])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # all-but-first
    unit = registry.create_unit('all-but-first')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', cdr)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # third-ele
    unit = registry.create_unit('third-ele')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', caddr)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # second-ele
    unit = registry.create_unit('second-ele')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', cadr)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('rarity', [0.85, 17, 3])
    unit.set_prop('worth', 500)

    # first-ele
    unit = registry.create_unit('first-ele')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', car)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # reverse-o-pair
    unit = registry.create_unit('reverse-o-pair')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['o-pair'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda p: [p[1], p[0]])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op', 'ord-struc-op', 'list-op'])
    unit.set_prop('range', ['o-pair'])
    unit.set_prop('worth', 500)

    # pair
    unit = registry.create_unit('pair')
    unit.set_prop('fast-defn', lambda s: isinstance(s, list) and len(s) == 2)
    unit.set_prop('generalizations', ['anything', 'structure', 'mult-ele-struc', 'un-ord-struc', 'bag'])
    unit.set_prop('generator', [[[]], ['get-a-o-pair'], ['old']])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('specializations', ['non-empty-struc'])
    unit.set_prop('worth', 500)

    # o-pair
    unit = registry.create_unit('o-pair')
    unit.set_prop('fast-defn', lambda s: isinstance(s, list) and len(s) == 2)
    unit.set_prop('generalizations', ['anything', 'structure', 'mult-ele-struc', 'ord-struc', 'list'])
    unit.set_prop('generator', [[[]], ['get-a-o-pair'], ['old']])
    unit.set_prop('in-domain-of', ['reverse-o-pair'])
    unit.set_prop('is-range-of', ['reverse-o-pair'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('specializations', ['non-empty-struc'])
    unit.set_prop('worth', 500)

    # parallel-join
    unit = registry.create_unit('parallel-join')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['type-of-structure', 'unary-op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', parallel_join)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'binary-op'])
    unit.set_prop('range', ['unary-op'])
    unit.set_prop('worth', 800)

    # parallel-join-2
    unit = registry.create_unit('parallel-join-2')
    unit.set_prop('arity', 3)
    unit.set_prop('domain', ['type-of-structure', 'type-of-structure', 'binary-op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', parallel_join_2)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'tertiary-op'])
    unit.set_prop('range', ['binary-op'])
    unit.set_prop('rarity', [0.3272727, 36, 74])
    unit.set_prop('worth', 800)

    # tertiary-op
    unit = registry.create_unit('tertiary-op')
    unit.set_prop('examples', ['parallel-replace-2', 'repeat2', 'parallel-join-2', 'proj-1-of-3', 'proj-2-of-3', 'proj-3-of-3'])
    unit.set_prop('fast-defn', lambda f: getattr(f, 'arity', 0) == 3)
    unit.set_prop('generalizations', ['op', 'anything'])
    unit.set_prop('in-domain-of', ['repeat2'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category', 'op-cat-by-nargs'])
    unit.set_prop('lower-arity', ['binary-op'])
    unit.set_prop('rarity', [0.3978495, 37, 56])
    unit.set_prop('specializations', ['tertiary-pred'])
    unit.set_prop('worth', 500)

    # repeat
    unit = registry.create_unit('repeat')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['type-of-structure', 'binary-op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', TODO("(lambda (s f) (cond ((and (memb 'structure (generalizations s)) (memb 'op (isa f)) (eq 2 (length (domain f))) (or (eq 'anything (cadr (domain f))) (let ((typmem (each-element-is-a s))) (and typmem (is-a-kind-of typmem (cadr (domain f)))))) (is-a-kind-of (car (range f)) (car (domain f)))) (let ((nam (create-unit (pack* 'repeat- f '-on- s 's)))) (put nam 'isa (let* ((r (isa f)) (r (subst 'unary-op 'binary-op r)) (r (subst 'unary-pred 'binary-pred r)) (r (subst 'constant-unary-pred 'constant-binary-pred r))) r)) (put nam 'worth (average-worths 'repeat (average-worths f s))) (put nam 'arity 1) (put nam 'domain (list s)) (put nam 'range (copy (range f))) (put nam 'unitized-alg (compile-report (subst f 'f '(lambda (s) (if (consp s) (let ((v (car s))) (mapc (lambda (e) (setf v (run-alg 'f v e))) (cdr s)) v) 'failed))))) (put nam 'elim-slots '(applics)) (put nam 'creditors 'repeat) (add-inv nam) nam)) (t 'failed)))"))
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'binary-op'])
    unit.set_prop('range', ['unary-op'])
    unit.set_prop('rarity', [0.3555556, 16, 29])
    unit.set_prop('worth', 800)

    # repeat2
    unit = registry.create_unit('repeat2')
    unit.set_prop('arity', 3)
    unit.set_prop('domain', ['type-of-structure', 'type-of-structure', 'tertiary-op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', TODO("(lambda (s s2 f) (cond ((and (memb 'structure (generalizations s)) (memb 'structure (generalizations s2)) (memb 'op (isa f)) (eq 3 (length (domain f))) (or (eq 'anything (caddr (domain f))) (let ((typmem (each-element-is-a s))) (and typmem (is-a-kind-of typmem (caddr (domain f)))))) (is-a-kind-of (car (range f)) (car (domain f))) (is-a-kind-of s2 (cadr (domain f)))) (let ((nam (create-unit (pack* 'repeat2- f '-on- 's-with-a- s2 '-as-param)))) (put nam 'isa (let* ((r (isa f)) (r (subst 'binary-op 'tertiary-op r)) (r (subst 'binary-pred 'teritiary-pred r))) r)) (put nam 'worth (average-worths 'repeat2 (average-worths f (average-worths s s2)))) (put nam 'arity 2) (put nam 'domain (list s s2)) (put nam 'range (copy (range f))) (put nam 'unitized-alg (compile-report (subst f 'f '(lambda (s s2) (if (consp s) (let ((v (car s))) (mapc (lambda (e) (setf v (run-alg 'f v s2 e))) (cdr s)) v) 'failed))))) (put nam 'elim-slots '(applics)) (put nam 'creditors '(repeat2)) (add-inv nam) nam)) (t 'failed)))"))
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'tertiary-op'])
    unit.set_prop('range', ['binary-op'])
    unit.set_prop('rarity', [0.2295082, 14, 47])
    unit.set_prop('worth', 800)

    # binary-op
    unit = registry.create_unit('binary-op')
    unit.set_prop('examples', ['parallel-replace', 'bag-difference', 'o-set-difference', 'list-difference', 'set-difference', 'struc-difference', 'bag-union', 'list-union', 'o-set-union', 'struc-union', 'bag-intersect', 'set-union', 'set-intersect', 'ord-struc-equal', 'bag-equal', 'list-equal', 'o-set-equal', 'o-set-delete', 'o-set-insert', 'mult-ele-struc-delete-1', 'bag-delete-1', 'bag-delete', 'bag-insert', 'list-delete-1', 'list-delete', 'list-insert', 'set-delete', 'set-insert', 'struc-delete', 'struc-insert', 'and', 'add', 'always-nil-2', 'always-t-2', 'compose', 'eq', 'equal', 'ieqp', 'igeq', 'igreaterp', 'ileq', 'ilessp', 'multiply', 'or', 'set-equal', 'struc-equal', 'subsetp', 'the-first-of', 'the-second-of', 'repeat', 'parallel-join', 'member', 'memb', 'proj1', 'proj2', 'implies', 'mult-ele-struc-insert'])
    unit.set_prop('fast-defn', lambda f: getattr(f, 'arity', 0) == 2)
    unit.set_prop('generalizations', ['op', 'anything'])
    unit.set_prop('higher-arity', ['tertiary-op'])
    unit.set_prop('in-domain-of', ['parallel-replace-2', 'repeat', 'parallel-join-2'])
    unit.set_prop('is-range-of', ['parallel-replace-2', 'repeat2', 'parallel-join-2'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category', 'op-cat-by-nargs'])
    unit.set_prop('lower-arity', ['unary-op'])
    unit.set_prop('rarity', [0.1827957, 17, 76])
    unit.set_prop('specializations', ['binary-pred'])
    unit.set_prop('worth', 500)

    # parallel-replace-2
    unit = registry.create_unit('parallel-replace-2')
    unit.set_prop('arity', 3)
    unit.set_prop('domain', ['type-of-structure', 'type-of-structure', 'binary-op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', TODO('(lambda (s s2 f) (cond ((and (memb \'structure (generalizations s)) (memb \'structure (generalizations s2)) (memb \'op (isa f)) (eq 2 (length (domain f))) (is-a-kind-of s2 (cadr (domain f))) (or (eq \'anything (car (domain f))) (let ((typmem (each-element-is-a s))) (and typmem (is-a-kind-of typmem (car (domain f))))))) (let ((nam (create-unit (pack* \'perform- f \'-on- s \'s-with-a- s2 \'-as-param)))) (put nam \'isa (isa f)) (put nam \'worth (average-worths \'parallel-replace-2 (average-worths f (average-worths s s2)))) (put nam \'arity 2) (put nam \'domain (list s s2)) (put nam \'range (list (let ((mu (pack* s \'-of- (car (range f)) \'s))) (cond ((unitp mu) mu) (t (cprin1 21 "~% It might be nice to have a unit called " mu "~%") s))))) (put nam \'unitized-alg (compile-report (subst f \'f \'(lambda (s s2) (mapcar (lambda (e) (run-alg \'f e s2)) s))))) (put nam \'elim-slots \'(applics)) (put nam \'creditors \'(parallel-replace-2)) (add-inv nam) nam)) (t \'failed)))'))
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'tertiary-op'])
    unit.set_prop('range', ['binary-op'])
    unit.set_prop('rarity', [0.375, 3, 5])
    unit.set_prop('worth', 800)

    # each-element-is-a
    unit = registry.create_unit('each-element-is-a')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # unary-op
    unit = registry.create_unit('unary-op')
    unit.set_prop('examples', ['coalesce', 'always-nil', 'always-t', 'best-choose', 'best-subset', 'constant-binary-pred', 'constant-unary-pred', 'divisors-of', 'good-choose', 'good-subset', 'random-choose', 'random-subset', 'square', 'successor', 'undefined-pred', 'reverse-o-pair', 'first-ele', 'second-ele', 'third-ele', 'all-but-first', 'all-but-second', 'all-but-third', 'last-ele', 'all-but-last', 'identity-1', 'restrict', 'invert-op', 'not'])
    unit.set_prop('fast-defn', lambda f: getattr(f, 'arity', 0) == 1)
    unit.set_prop('generalizations', ['op', 'anything'])
    unit.set_prop('higher-arity', ['binary-op'])
    unit.set_prop('in-domain-of', ['parallel-replace', 'parallel-join'])
    unit.set_prop('is-range-of', ['parallel-replace', 'repeat', 'parallel-join'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category', 'op-cat-by-nargs'])
    unit.set_prop('rarity', [0.2473118, 23, 70])
    unit.set_prop('specializations', ['unary-pred'])
    unit.set_prop('worth', 500)

    # type-of-structure
    unit = registry.create_unit('type-of-structure')
    unit.set_prop('examples', ['set', 'list', 'bag', 'mult-ele-struc', 'o-set', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc', 'o-pair', 'pair', 'empty-struc', 'non-empty-struc'])
    unit.set_prop('generalizations', ['category'])
    unit.set_prop('in-domain-of', ['parallel-replace', 'parallel-replace-2', 'repeat', 'repeat2', 'parallel-join', 'parallel-join-2'])
    unit.set_prop('isa', ['category', 'anything', 'repr-concept'])
    unit.set_prop('worth', 500)

    # parallel-replace
    unit = registry.create_unit('parallel-replace')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['type-of-structure', 'unary-op'])
    unit.set_prop('elim-slots', ['applics'])
    def parallel_replace(s, f, registry):
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
                
        # Create new unit name
        new_name = f'perform-{f.name}-on-{s.name}s'
        new_unit = registry.create_unit(new_name)
        
        # Copy properties
        new_unit.set_prop('isa', list(getattr(f, 'isa', [])))
        new_unit.set_prop('worth', (getattr(f, 'worth', 500) + getattr(s, 'worth', 500)) // 2)
        new_unit.set_prop('arity', 1)
        new_unit.set_prop('domain', [s.name])
        
        # Set range based on input function's range
        f_range = getattr(f, 'range', [])[0] if getattr(f, 'range', []) else s.name
        new_unit.set_prop('range', [f'{s.name}-of-{f_range}-s'])
        
        # Define the algorithm that applies f to each element
        def apply_to_all(struct):
            return [run_alg(f.name, e) for e in struct]
        new_unit.set_prop('unitized-alg', apply_to_all)
        
        # Set administrative properties
        new_unit.set_prop('elim-slots', ['applics'])
        new_unit.set_prop('creditors', ['parallel-replace'])
        
        return new_unit

    unit.set_prop('fast-alg', parallel_replace)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'binary-op'])
    unit.set_prop('range', ['unary-op'])
    unit.set_prop('rarity', [0.2372881, 14, 45])
    unit.set_prop('worth', 888)

    # coalesce
    unit = registry.create_unit('coalesce')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', TODO("(lambda (f) (let ((coargs (random-pair (domain f) 'is-a-kind-of))) (cond (coargs (let ((nam (create-unit (pack* 'coa- f)))) (put nam 'isa (set-diff (isa f) (examples 'op-cat-by-nargs))) (put nam 'worth (average-worths 'coalesce f)) (put nam 'arity (1- (arity f))) (let* ((fargs (mapcar \\#\\'the-second-of (domain f) '(u v w x y z z2 z3 z4 z5))) (newargs (copy fargs))) (rplaca (nth newargs (cadr coargs)) (car (nth newargs (car coargs)))) (let ((newdom (copy (domain f)))) (rplaca (nth newdom (cadr coargs)) (car (nth newdom (car coargs)))) (if (<= (cadr coargs) 1) (pop newdom) (rplacd (nth newdom (1- (cadr coargs))) (cdr (nth newdom (cadr coargs))))) (if (<= (cadr coargs) 1) (pop fargs) (rplacd (nth fargs (1- (cadr coargs))) (cdr (nth fargs (cadr coargs))))) (put nam 'domain newdom) (put nam 'range (copy (range f))) (put nam 'unitized-alg (compile-report \\` (lambda \\,fargs (run-alg '\\,f \\,@newargs)))) (put nam 'elim-slots '(applics)) (put nam 'creditors '(coalesce)) (put nam 'isa (append (isa nam) (subset (examples 'op-cat-by-nargs) (lambda (pc) (run-defn pc nam))))) (add-inv nam) nam)))) (t 'failed))))"))
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'unary-op'])
    unit.set_prop('range', ['op'])
    unit.set_prop('rarity', [0.3928571, 22, 34])
    unit.set_prop('worth', 900)

    # bag-difference
    unit = registry.create_unit('bag-difference')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['bag', 'bag'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['struc-difference'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'bag-op', 'binary-op'])
    unit.set_prop('range', ['bag'])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((null s1) ()) ((member (car s2) s2) (run-alg 'bag-delete-1 (car s1) s2)) (t (cons (car s1) (run-alg 'bag-difference (cdr s1) (run-alg 'bag-delete-1 (car s2) s2))))))"))
    unit.set_prop('worth', 500)

    # o-set-difference
    unit = registry.create_unit('o-set-difference')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['o-set', 'o-set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', set_difference)
    unit.set_prop('generalizations', ['struc-difference'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'o-set-op', 'binary-op'])
    unit.set_prop('range', ['o-set'])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((null s1) ()) ((member (car s1) s2) (run-alg 'o-set-difference (cdr s1) s2)) (t (cons (car s1) (run-alg 'o-set-difference (cdr s1) s2)))))"))
    unit.set_prop('worth', 500)

    # list-difference
    unit = registry.create_unit('list-difference')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['list', 'list'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['struc-difference'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'list-op', 'binary-op'])
    unit.set_prop('range', ['list'])
    unit.set_prop('recursive-alg', lambda s1, s2: [] if not s1 else 
        (run_alg('list-difference', s1[1:], run_alg('list-delete-1', s1[0], s2))
         if member(s1[0], s2)
         else [s2[0]] + run_alg('list-difference', s1[1:], run_alg('list-delete-1', s1[0], s2))))
    unit.set_prop('worth', 500)

    # set-difference
    unit = registry.create_unit('set-difference')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['set', 'set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', set_difference)
    unit.set_prop('generalizations', ['struc-difference'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'set-op', 'binary-op'])
    unit.set_prop('range', ['set'])
    unit.set_prop('recursive-alg', lambda s1, s2: [] if not s1 else (run_alg('set-difference', s1[1:], s2) if member(s1[0], s2) else [s1[0]] + run_alg('set-difference', s1[1:], s2)))
    unit.set_prop('worth', 500)

    # struc-difference
    unit = registry.create_unit('struc-difference')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['structure', 'structure'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'binary-op'])
    unit.set_prop('range', ['structure'])
    unit.set_prop('specializations', ['set-difference', 'list-difference', 'o-set-difference', 'bag-difference'])
    unit.set_prop('worth', 500)

    # bag-union
    unit = registry.create_unit('bag-union')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['bag', 'bag'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['struc-union'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'binary-op'])
    unit.set_prop('range', ['bag'])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((null s1) s2) (t (run-alg 'bag-insert (car s1) (run-alg 'bag-union (cdr s1) (run-alg 'bag-delete-1 (car s1) s2))))))"))
    unit.set_prop('worth', 500)

    # list-union
    unit = registry.create_unit('list-union')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['list', 'list'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', append)
    unit.set_prop('generalizations', ['struc-union'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'list-op', 'binary-op'])
    unit.set_prop('range', ['list'])
    unit.set_prop('recursive-alg', lambda s1, s2: s2 if not s1 else [s1[0]] + run_alg('list-union', s1[1:], s2))
    unit.set_prop('worth', 500)

    # o-set-union
    unit = registry.create_unit('o-set-union')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['o-set', 'o-set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', set_union)
    unit.set_prop('generalizations', ['struc-union'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'o-set-op', 'binary-op'])
    unit.set_prop('range', ['o-set'])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((null s1) s2) ((member (car s1) s2) (run-alg 'o-set-union (cdr s1) s2)) (t (cons (car s1) (run-alg 'o-set-union (cdr s1) s2)))))"))
    unit.set_prop('worth', 500)

    # struc-union
    unit = registry.create_unit('struc-union')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['structure', 'structure'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'binary-op'])
    unit.set_prop('range', ['structure'])
    unit.set_prop('specializations', ['set-union', 'o-set-union', 'list-union', 'bag-union'])
    unit.set_prop('worth', 500)

    # bag-intersect
    unit = registry.create_unit('bag-intersect')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['bag', 'bag'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['struc-intersect'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'bag-op', 'binary-op'])
    unit.set_prop('iterative-alg', TODO("(lambda (s1 s2) (dolist (x (copy-list s1)) (cond ((member x s2) (setf s2 (run-alg 'bag-delete-1 x s2))) (t (setf s1 (run-alg 'bag-delete-1 x s1))))) s1)"))
    unit.set_prop('range', ['bag'])
    unit.set_prop('worth', 500)

    # o-set-intersect
    unit = registry.create_unit('o-set-intersect')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['o-set', 'o-set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['struc-intersect'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'o-set-op', 'binary-op'])
    unit.set_prop('range', ['o-set'])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((null s1) ()) ((member (car s1) s2) (cons (car s1) (run-alg 'o-set-intersect (cdr s1) s2))) (t (run-alg 'o-set-intersect (cdr s1) s2))))"))
    unit.set_prop('worth', 500)

    # list-intersect
    unit = registry.create_unit('list-intersect')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['list', 'list'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['struc-intersect'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'list-op', 'binary-op'])
    unit.set_prop('range', ['list'])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((null s1) ()) ((member (car s1) s2) (cons (car s1) (run-alg 'list-intersect (cdr s1) (run-alg 'list-delete-1 (car s1) s2)))) (t (run-alg 'list-intersect (cdr s1) s2))))"))
    unit.set_prop('worth', 500)

    # struc-intersect
    unit = registry.create_unit('struc-intersect')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['structure', 'structure'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'binary-op'])
    unit.set_prop('range', ['structure'])
    unit.set_prop('specializations', ['set-intersect', 'list-intersect', 'o-set-intersect', 'bag-intersect'])
    unit.set_prop('worth', 500)

    # set-union
    unit = registry.create_unit('set-union')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['set', 'set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', set_union)
    unit.set_prop('generalizations', ['struc-union'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'set-op', 'binary-op'])
    unit.set_prop('range', ['set'])
    unit.set_prop('recursive-alg', lambda s1, s2: s2 if not s1 else (run_alg('set-union', s1[1:], s2) if member(s1[0], s2) else [s1[0]] + run_alg('set-union', s1[1:], s2)))
    unit.set_prop('worth', 500)

    # set-intersect
    unit = registry.create_unit('set-intersect')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['set', 'set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', set_intersect)
    unit.set_prop('generalizations', ['struc-intersect'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'anything', 'struc-op', 'set-op', 'binary-op'])
    unit.set_prop('range', ['set'])
    unit.set_prop('recursive-alg', lambda s1, s2: [] if not s1 else ([s1[0]] + run_alg('set-intersect', s1[1:], s2) if member(s1[0], s2) else run_alg('set-intersect', s1[1:], s2)))
    unit.set_prop('worth', 500)

    # ord-struc-op
    unit = registry.create_unit('ord-struc-op')
    unit.set_prop('abbrev', ['Operations on structures which are ordered'])
    unit.set_prop('examples', ['ord-struc-equal', 'reverse-o-pair'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything', 'struc-op'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['list-op', 'o-set-op'])
    unit.set_prop('worth', 500)

    # ord-struc-equal
    unit = registry.create_unit('ord-struc-equal')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['ord-struc', 'ord-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', equals)
    unit.set_prop('isa', ['math-concept', 'math-op', 'anything', 'struc-op', 'ord-struc-op', 'binary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['list-equal', 'o-set-equal'])
    unit.set_prop('worth', 500)

    # bag-equal
    unit = registry.create_unit('bag-equal')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['bag', 'bag'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['equal', 'struc-equal'])
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'struc-op', 'bag-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.1, 1, 9])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((and (null s1) (null s2)) t) (t (and (consp s1) (consp s2) (member (car s1) s2) (run-alg 'bag-equal (cdr s1) (run-alg 'bag-delete-1 (car s1) s2))))))"))
    unit.set_prop('specializations', ['list-equal'])
    unit.set_prop('worth', 500)

    # list-equal
    unit = registry.create_unit('list-equal')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['list', 'list'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', equals)
    unit.set_prop('generalizations', ['equal', 'struc-equal', 'bag-equal', 'ord-struc-equal'])
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'struc-op', 'list-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.1, 1, 9])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((and (null s1) (null s2)) t) (t (and (consp s1) (consp s2) (equal (car s1) (car s2)) (run-alg 'list-equal (cdr s1) (cdr s2))))))"))
    unit.set_prop('worth', 500)

    # o-set-equal
    unit = registry.create_unit('o-set-equal')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['o-set', 'o-set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', equals)
    unit.set_prop('generalizations', ['equal', 'struc-equal', 'subsetp', 'set-equal', 'ord-struc-equal'])
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'struc-op', 'o-set-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.1, 1, 9])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((and (null s1) (null s2)) t) (t (and (consp s1) (consp s2) (equal (car s1) (car s2)) (run-alg 'o-set-equal (cdr s1) (cdr s2))))))"))
    unit.set_prop('worth', 500)

    # suf-defn
    unit = registry.create_unit('suf-defn')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('generalizations', ['defn'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['defn'])
    unit.set_prop('worth', 600)

    # nec-defn
    unit = registry.create_unit('nec-defn')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('generalizations', ['defn'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['defn'])
    unit.set_prop('worth', 600)

    # un-ord-struc
    unit = registry.create_unit('un-ord-struc')
    unit.set_prop('generalizations', ['structure', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('specializations', ['bag', 'set', 'pair', 'empty-struc', 'non-empty-struc'])
    unit.set_prop('worth', 500)

    # ord-struc
    unit = registry.create_unit('ord-struc')
    unit.set_prop('generalizations', ['structure', 'anything'])
    unit.set_prop('in-domain-of', ['ord-struc-equal', 'all-but-first', 'first-ele', 'second-ele', 'third-ele', 'all-but-second', 'all-but-third', 'last-ele', 'all-but-last'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('specializations', ['list', 'o-set', 'o-pair', 'empty-struc', 'non-empty-struc'])
    unit.set_prop('worth', 500)

    # no-mult-ele-struc
    unit = registry.create_unit('no-mult-ele-struc')
    unit.set_prop('generalizations', ['structure', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('nec-defn', no_repeats_in)
    unit.set_prop('specializations', ['set', 'o-set', 'empty-struc', 'non-empty-struc'])
    unit.set_prop('worth', 500)

    # o-set-delete
    unit = registry.create_unit('o-set-delete')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'o-set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', remove_)
    unit.set_prop('generalizations', ['struc-delete'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'o-set-op', 'binary-op'])
    unit.set_prop('range', ['o-set'])
    unit.set_prop('recursive-alg', TODO("(lambda (x s) (cond ((null s) ()) ((equal x (car s)) (cdr s)) (t (cons (car s) (run-alg 'o-set-delete x (cdr s))))))"))
    unit.set_prop('worth', 500)

    # o-set-op
    unit = registry.create_unit('o-set-op')
    unit.set_prop('abbrev', ['O-Set Operations'])
    unit.set_prop('examples', ['o-set-insert', 'o-set-delete', 'o-set-equal', 'o-set-intersect', 'o-set-union', 'o-set-difference'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything', 'struc-op', 'ord-struc-op'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # o-set-insert
    unit = registry.create_unit('o-set-insert')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'o-set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', TODO("(lambda (x s) (cond ((member x s) s) ((null s) (cons x s)) (t (cons (car s) (run-alg 'o-set-insert x (cdr s))))))"))
    unit.set_prop('generalizations', ['struc-insert'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'o-set-op', 'binary-op'])
    unit.set_prop('range', ['o-set'])
    unit.set_prop('recursive-alg', TODO("(lambda (x s) (cond ((null s) (cons x s)) ((equal x (car s)) s) (t (cons (car s) (run-alg 'o-set-insert x (cdr s))))))"))
    unit.set_prop('worth', 500)

    # o-set
    unit = registry.create_unit('o-set')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', lambda s: not s or no_repeats_in(s))
    unit.set_prop('generalizations', ['anything', 'structure', 'bag', 'list', 'set', 'no-mult-ele-struc', 'ord-struc'])
    unit.set_prop('generator', [[[]], ['get-a-set'], ['old']])
    unit.set_prop('in-domain-of', ['o-set-insert', 'o-set-delete', 'o-set-equal', 'o-set-intersect', 'o-set-union', 'o-set-difference'])
    unit.set_prop('is-range-of', ['o-set-insert', 'o-set-delete', 'o-set-intersect', 'o-set-union', 'o-set-difference'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('rarity', [0, 2, 2])
    unit.set_prop('recursive-defn', lambda s: (not member(s[0], s[1:]) and run_defn('o-set', s[1:])) if consp(s) else null(s))
    unit.set_prop('specializations', ['empty-struc', 'non-empty-struc'])
    unit.set_prop('worth', 500)

    # mult-ele-struc-delete-1
    unit = registry.create_unit('mult-ele-struc-delete-1')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'mult-ele-struc'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'mult-ele-struc-op', 'binary-op'])
    unit.set_prop('range', ['mult-ele-struc'])
    unit.set_prop('recursive-alg', TODO("(lambda (x s) (cond ((null s) ()) ((equal x (car s)) (cdr s)) (t (cons (car s) (run-alg 'mult-ele-struc-delete-1 x (cdr s))))))"))
    unit.set_prop('specializations', ['list-delete-1', 'bag-delete-1'])
    unit.set_prop('worth', 500)

    # mult-ele-struc-op
    unit = registry.create_unit('mult-ele-struc-op')
    unit.set_prop('abbrev', ['Operations on structures which have multiple elements'])
    unit.set_prop('examples', ['mult-ele-struc-delete-1', 'mult-ele-struc-insert'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything', 'struc-op'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['list-op', 'bag-op'])
    unit.set_prop('worth', 500)

    # mult-ele-struc
    unit = registry.create_unit('mult-ele-struc')
    unit.set_prop('generalizations', ['structure', 'anything'])
    unit.set_prop('in-domain-of', ['mult-ele-struc-delete-1', 'mult-ele-struc-insert'])
    unit.set_prop('is-range-of', ['mult-ele-struc-delete-1', 'mult-ele-struc-insert'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('specializations', ['list', 'bag', 'o-pair', 'pair', 'empty-struc', 'non-empty-struc'])
    unit.set_prop('suf-defn', repeats_in)
    unit.set_prop('worth', 500)

    # bag-delete-1
    unit = registry.create_unit('bag-delete-1')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'bag'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['mult-ele-struc-delete-1'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'bag-op', 'binary-op'])
    unit.set_prop('range', ['bag'])
    unit.set_prop('recursive-alg', TODO("(lambda (x s) (cond ((null s) ()) ((equal x (car s)) (cdr s)) (t (cons (car s) (run-alg 'bag-delete-1 x (cdr s))))))"))
    unit.set_prop('worth', 500)

    # bag-delete
    unit = registry.create_unit('bag-delete')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'bag'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', remove_)
    unit.set_prop('generalizations', ['struc-delete'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'bag-op', 'binary-op'])
    unit.set_prop('range', ['bag'])
    unit.set_prop('recursive-alg', TODO("(lambda (x s) (cond ((null s) ()) ((equal x (car s)) (run-alg 'bag-delete x (cdr s))) (t (cons (car s) (run-alg 'bag-delete x (cdr s))))))"))
    unit.set_prop('worth', 500)

    # bag-op
    unit = registry.create_unit('bag-op')
    unit.set_prop('abbrev', ['Bag Operations'])
    unit.set_prop('examples', ['bag-insert', 'bag-delete', 'bag-delete-1', 'bag-equal', 'bag-intersect', 'bag-union', 'bag-difference'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything', 'struc-op', 'mult-ele-struc-op'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # bag-insert
    unit = registry.create_unit('bag-insert')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'bag'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', cons)
    unit.set_prop('generalizations', ['struc-insert', 'mult-ele-struc-insert'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'bag-op', 'binary-op'])
    unit.set_prop('range', ['bag'])
    unit.set_prop('worth', 500)

    # bag
    unit = registry.create_unit('bag')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', listp)
    unit.set_prop('generalizations', ['anything', 'structure', 'mult-ele-struc', 'un-ord-struc'])
    unit.set_prop('generator', [[[]], ['get-a-list'], ['old']])
    unit.set_prop('in-domain-of', ['bag-insert', 'bag-delete', 'bag-delete-1', 'bag-equal', 'bag-intersect', 'bag-union', 'bag-difference'])
    unit.set_prop('is-range-of', ['bag-insert', 'bag-delete', 'bag-delete-1', 'bag-intersect', 'bag-union', 'bag-difference'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('rarity', [0, 2, 2])
    unit.set_prop('recursive-defn', TODO("(lambda (s) (cond ((not (consp s)) (eq s ())) (t (run-defn 'bag (cdr s)))))"))
    unit.set_prop('specializations', ['set', 'o-set', 'pair', 'empty-struc', 'non-empty-struc'])
    unit.set_prop('worth', 500)

    # list-delete-1
    unit = registry.create_unit('list-delete-1')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'list'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['mult-ele-struc-delete-1'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'anything', 'struc-op', 'list-op', 'binary-op'])
    unit.set_prop('range', ['list'])
    unit.set_prop('recursive-alg', lambda x, s: [] if not s else (s[1:] if equals(x, s[0]) else [s[0]] + run_alg('list-delete-1', x, s[1:])))
    unit.set_prop('worth', 500)

    # list-delete
    unit = registry.create_unit('list-delete')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'list'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', remove_)
    unit.set_prop('generalizations', ['struc-delete'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'list-op', 'binary-op'])
    unit.set_prop('range', ['list'])
    unit.set_prop('recursive-alg', lambda x, s: [] if not s else ([s[0]] + run_alg('list-delete', x, s[1:]) if not equals(x, s[0]) else run_alg('list-delete', x, s[1:])))
    unit.set_prop('worth', 500)

    # list
    unit = registry.create_unit('list')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', listp)
    unit.set_prop('generalizations', ['anything', 'structure', 'mult-ele-struc', 'ord-struc'])
    unit.set_prop('generator', [[[]], ['get-a-list'], ['old']])
    unit.set_prop('in-domain-of', ['list-insert', 'list-delete', 'list-delete-1', 'list-equal', 'list-intersect', 'list-union', 'list-difference'])
    unit.set_prop('is-range-of', ['list-insert', 'list-delete', 'list-delete-1', 'list-intersect', 'list-union', 'list-difference'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('rarity', [0, 2, 2])
    unit.set_prop('recursive-defn', TODO("(lambda (s) (cond ((not (consp s)) (eq s ())) (t (run-defn 'list (cdr s)))))"))
    unit.set_prop('specializations', ['set', 'o-set', 'o-pair', 'empty-struc', 'non-empty-struc'])
    unit.set_prop('worth', 500)

    # list-insert
    unit = registry.create_unit('list-insert')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'list'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', cons)
    unit.set_prop('generalizations', ['struc-insert', 'mult-ele-struc-insert'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'list-op', 'binary-op'])
    unit.set_prop('range', ['list'])
    unit.set_prop('worth', 500)

    # list-op
    unit = registry.create_unit('list-op')
    unit.set_prop('abbrev', ['List Operations'])
    unit.set_prop('examples', ['list-insert', 'list-delete', 'list-delete-1', 'list-equal', 'list-intersect', 'list-union', 'list-difference', 'reverse-o-pair'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything', 'struc-op', 'mult-ele-struc-op', 'ord-struc-op'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # set-delete
    unit = registry.create_unit('set-delete')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', remove_)
    unit.set_prop('generalizations', ['struc-delete'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'set-op', 'binary-op'])
    unit.set_prop('range', ['set'])
    unit.set_prop('recursive-alg', TODO("(lambda (x s) (cond ((null s) ()) ((equal x (car s)) (cdr s)) (t (cons (car s) (run-alg 'set-delete x (cdr s))))))"))
    unit.set_prop('worth', 500)

    # set-insert
    unit = registry.create_unit('set-insert')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, s: s if member(x, s) else [x] + s)
    unit.set_prop('generalizations', ['struc-insert'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'set-op', 'binary-op'])
    unit.set_prop('range', ['set'])
    unit.set_prop('recursive-alg', TODO("(lambda (x s) (cond ((null s) (cons x s)) ((equal x (car s)) s) (t (cons (car s) (run-alg 'set-insert x (cdr s))))))"))
    unit.set_prop('worth', 500)

    # struc-delete
    unit = registry.create_unit('struc-delete')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'structure'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'binary-op'])
    unit.set_prop('range', ['structure'])
    unit.set_prop('specializations', ['list-delete', 'bag-delete', 'set-delete', 'o-set-delete'])
    unit.set_prop('worth', 500)

    # struc-op
    unit = registry.create_unit('struc-op')
    unit.set_prop('abbrev', ['Operations on structures'])
    unit.set_prop('examples', ['struc-insert', 'struc-delete', 'random-choose', 'random-subset', 'good-choose', 'best-choose', 'best-subset', 'good-subset', 'set-insert', 'set-delete', 'list-insert', 'list-delete', 'list-delete-1', 'bag-insert', 'bag-delete', 'bag-delete-1', 'mult-ele-struc-delete-1', 'o-set-insert', 'o-set-delete', 'o-set-equal', 'set-equal', 'bag-equal', 'list-equal', 'ord-struc-equal', 'set-intersect', 'set-union', 'struc-intersect', 'list-intersect', 'o-set-intersect', 'bag-intersect', 'struc-union', 'o-set-union', 'list-union', 'bag-union', 'struc-difference', 'set-difference', 'list-difference', 'o-set-difference', 'bag-difference', 'mult-ele-struc-insert'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['set-op', 'list-op', 'bag-op', 'mult-ele-struc-op', 'o-set-op', 'ord-struc-op', 'logic-op'])
    unit.set_prop('worth', 500)

    # struc-insert
    unit = registry.create_unit('struc-insert')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'structure'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'struc-op', 'binary-op'])
    unit.set_prop('range', ['structure'])
    unit.set_prop('specializations', ['list-insert', 'bag-insert', 'set-insert', 'o-set-insert'])
    unit.set_prop('worth', 500)

    # and
    unit = registry.create_unit('and')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: x and y)
    unit.set_prop('generalizations', ['the-second-of', 'the-first-of', 'or'])
    unit.set_prop('isa', ['op', 'pred', 'math-op', 'math-pred', 'anything', 'binary-op', 'logic-op', 'binary-pred'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('rarity', [1.0, 2, 0])
    unit.set_prop('worth', 569)

    # abbrev
    unit = registry.create_unit('abbrev')
    unit.set_prop('data-type', STRING)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 307)

    # add
    unit = registry.create_unit('add')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['nnumber', 'nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: x + y)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'num-op', 'anything', 'binary-op'])
    unit.set_prop('iterative-alg', lambda x, y: sum(1 for _ in range(x)))
    unit.set_prop('range', ['nnumber'])
    unit.set_prop('recursive-alg', TODO("(lambda (x y) (cond ((eq x 0) y) (t (run-alg 'successor (run-alg 'add (1- x) y)))))"))
    unit.set_prop('unitized-alg', TODO("(lambda (x y) (cond ((eq x 0) y) (t (run-alg 'successor (run-alg 'add (1- x) y)))))"))
    unit.set_prop('worth', 500)

    # alg
    unit = registry.create_unit('alg')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('sub-slots', ['fast-alg', 'iterative-alg', 'recursive-alg', 'unitized-alg'])
    unit.set_prop('worth', 600)

    # always-nil
    unit = registry.create_unit('always-nil')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x: None)
    unit.set_prop('generalizations', ['constant-unary-pred'])
    unit.set_prop('isa', ['op', 'pred', 'anything', 'constant-pred', 'unary-op', 'math-op', 'unary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('worth', 500)

    # always-nil-2
    unit = registry.create_unit('always-nil-2')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: None)
    unit.set_prop('generalizations', ['constant-binary-pred'])
    unit.set_prop('isa', ['op', 'pred', 'anything', 'constant-pred', 'binary-op', 'math-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('worth', 500)

    # always-t
    unit = registry.create_unit('always-t')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x: True)
    unit.set_prop('generalizations', ['constant-unary-pred'])
    unit.set_prop('isa', ['op', 'pred', 'anything', 'constant-pred', 'unary-op', 'math-op', 'unary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('worth', 500)

    # always-t-2
    unit = registry.create_unit('always-t-2')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: True)
    unit.set_prop('generalizations', ['constant-binary-pred'])
    unit.set_prop('isa', ['op', 'pred', 'anything', 'constant-pred', 'binary-op', 'math-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('worth', 500)

    # anything
    unit = registry.create_unit('anything')
    unit.set_prop('examples', ['and', 'or', 'the-first-of', 'the-second-of', 'square', 'divisors-of', 'multiply-add', 'successor', 'random-choose', 'random-subset', 'good-choose', 'best-choose', 'best-subset', 'good-subset', 'equal', 'ieqp', 'eq', 'ileq', 'igeq', 'ilessp', 'igreaterp', 'los1', 'los2', 'los3', 'los4', 'los5', 'los6', 'los7', 'win1', True, [], 'proto-conjec', 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 6, 28, 'if-about-to-work-on-task', 'applics', 'if-finished-working-on-task', 'isa', 'if-truly-relevant', 'sub-slots', 'if-parts', 'if-potentially-relevant', 'examples', 'data-type', 'english', 'worth', 'inverse', 'creditors', 'generalizations', 'specializations', 'then-add-to-agenda', 'then-compute', 'then-conjecture', 'abbrev', 'then-define-new-concepts', 'then-modify-slots', 'then-print-to-user', 'then-parts', 'super-slots', 'if-task-parts', 'format', 'dont-copy', 'double-check', 'generator', 'if-working-on-task', 'is-range-of', 'to-delete-1', 'alg', 'fast-defn', 'recursive-defn', 'unitized-defn', 'fast-alg', 'iterative-alg', 'recursive-alg', 'unitized-alg', 'iterative-defn', 'to-delete', 'applic-generator', 'arity', 'non-examples', 'compiled-defn', 'elim-slots', 'in-domain-of', 'domain', 'range', 'indirect-applics', 'direct-applics', 'defn', 'sib-slots', 'transpose', 'then-delete-old-concepts', 'subsumes', 'subsumed-by', 'overall-record', 'then-print-to-user-failed-record', 'then-add-to-agenda-failed-record', 'then-delete-old-concepts-failed-record', 'then-define-new-concepts-failed-record', 'then-conjecture-failed-record', 'then-modify-slots-failed-record', 'then-compute-failed-record', 'then-print-to-user-record', 'then-add-to-agenda-record', 'then-delete-old-concepts-record', 'then-define-new-concepts-record', 'then-conjecture-record', 'then-modify-slots-record', 'then-compute-record', 'record-for', 'failed-record-for', 'record', 'failed-record', 'h1', 'h5', 'h6', 'h3', 'h4', 'h7', 'h8', 'h9', 'h10', 'h11', 'h2', 'h12', 'h-avoid', 'h-avoid-2', 'h-avoid-3', 'h13', 'h14', 'h15', 'h16', 'h17', 'h18', 'h19', 'h-avoid-2-and', 'h-avoid-3-first', 'h-avoid-if-working', 'h5-criterial', 'h5-good', 'h19-criterial', 'set', 'heuristic', 'anything', 'math-concept', 'slot', 'math-obj', 'nnumber', 'unit', 'prime-num', 'conjecture', 'repr-concept', 'even-num', 'task', 'math-op', 'odd-num', 'perf-num', 'perf-square', 'op', 'set-of-numbers', 'set-op', 'unit-op', 'num-op', 'criterial-slot', 'pred', 'math-pred', 'bit', 'non-criterial-slot', 'hind-sight-rule', 'unary-unit-op', 'record-slot', 'h20', 'conjectures', 'h21', 'conjecture-about', 'structure', 'category', 'struc-equal', 'set-equal', 'subsetp', 'constant-pred', 'always-t', 'always-nil', 'constant-binary-pred', 'always-t-2', 'always-nil-2', 'constant-unary-pred', 'compose', 'undefined-pred', 'struc-insert', 'struc-op', 'struc-delete', 'set-insert', 'set-delete', 'list-op', 'list', 'list-insert', 'list-delete', 'list-delete-1', 'bag', 'bag-op', 'bag-insert', 'bag-delete', 'bag-delete-1', 'mult-ele-struc', 'mult-ele-struc-op', 'mult-ele-struc-delete-1', 'o-set', 'o-set-insert', 'o-set-op', 'o-set-delete', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc', 'nec-defn', 'suf-defn', 'o-set-equal', 'bag-equal', 'list-equal', 'ord-struc-op', 'ord-struc-equal', 'set-intersect', 'set-union', 'struc-intersect', 'list-intersect', 'o-set-intersect', 'bag-intersect', 'struc-union', 'o-set-union', 'list-union', 'bag-union', 'struc-difference', 'set-difference', 'list-difference', 'o-set-difference', 'bag-difference', 'coalesce', 'type-of-structure', 'unary-op', 'parallel-replace', 'each-element-is-a', 'binary-op', 'parallel-replace-2', 'repeat', 'tertiary-op', 'repeat2', 'parallel-join', 'parallel-join-2', 'o-pair', 'pair', 'reverse-o-pair', 'first-ele', 'second-ele', 'third-ele', 'all-but-first', 'all-but-second', 'all-but-third', 'last-ele', 'all-but-last', 'member', 'memb', 'proj1', 'proj2', 'proj-1-of-3', 'proj-2-of-3', 'proj-3-of-3', 'identity-1', 'restrict', 'inverted-op', 'invert-op', 'set-of-o-pairs', 'relation', 'logic-op', 'not', 'implies', 'atom', 'truth-value', 'structure-of-structures', 'set-of-sets', 'empty-struc', 'non-empty-struc', 'undefined', 'lower-arity', 'higher-arity', 'unary-pred', 'binary-pred', 'tertiary-pred', 'pred-cat-by-nargs', 'op-cat-by-nargs', 'extensions', 'restrictions', 'interestingness', 'h22', 'more-interesting', 'less-interesting', 'int-examples', 'h23', 'h24', 'why-int', 'rarity', 'is-a-int', 'h25', 'h26', 'h27', 28, 'h29', 'mult-ele-struc-insert', 'int-applics', 'english-1', 'restrict-random-subset-3'])
    unit.set_prop('fast-defn', lambda x: True)
    unit.set_prop('in-domain-of', ['equal', 'eq', 'and', 'or', 'the-second-of', 'the-first-of', 'always-t', 'always-nil', 'constant-binary-pred', 'always-t-2', 'always-nil-2', 'constant-unary-pred', 'undefined-pred', 'struc-insert', 'struc-delete', 'set-insert', 'set-delete', 'list-insert', 'list-delete', 'list-delete-1', 'bag-insert', 'bag-delete', 'bag-delete-1', 'mult-ele-struc-delete-1', 'o-set-insert', 'o-set-delete', 'member', 'memb', 'proj1', 'proj2', 'proj-1-of-3', 'proj-2-of-3', 'proj-3-of-3', 'identity-1', 'not', 'implies', 'mult-ele-struc-insert'])
    unit.set_prop('is-range-of', ['random-choose', 'good-choose', 'best-choose', 'and', 'or', 'the-second-of', 'the-first-of', 'first-ele', 'second-ele', 'third-ele', 'all-but-first', 'all-but-second', 'all-but-third', 'last-ele', 'all-but-last', 'proj1', 'proj2', 'proj-1-of-3', 'proj-2-of-3', 'proj-3-of-3', 'identity-1', 'implies', 'ord-struc-equal'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('rarity', [1, 12, 0])
    unit.set_prop('specializations', ['set', 'heuristic', 'slot', 'nnumber', 'unit', 'prime-num', 'conjecture', 'even-num', 'task', 'odd-num', 'perf-num', 'perf-square', 'set-of-numbers', 'criterial-slot', 'bit', 'non-criterial-slot', 'hind-sight-rule', 'unary-unit-op', 'math-concept', 'repr-concept', 'math-op', 'math-obj', 'set-op', 'unit-op', 'num-op', 'math-pred', 'op', 'pred', 'record-slot', 'structure', 'constant-pred', 'struc-op', 'list-op', 'list', 'bag', 'bag-op', 'mult-ele-struc-op', 'mult-ele-struc', 'o-set', 'o-set-op', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc', 'ord-struc-op', 'unary-op', 'binary-op', 'tertiary-op', 'o-pair', 'pair', 'inverted-op', 'set-of-o-pairs', 'relation', 'logic-op', 'atom', 'truth-value', 'structure-of-structures', 'set-of-sets', 'empty-struc', 'non-empty-struc', 'unary-pred', 'binary-pred', 'tertiary-pred'])
    unit.set_prop('worth', 550)

    # applic-generator
    unit = registry.create_unit('applic-generator')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('format', ['applic-gen-init', 'applic-gen-build', 'applic-gen-args'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # applics
    unit = registry.create_unit('applics')
    unit.set_prop('data-type', IO_PAIR)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('format', [['situation', 'resultant-units', 'directness'], ['situation', 'resultant-units', 'directness'], 'etc.'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('more-interesting', ['int-applics'])
    unit.set_prop('sub-slots', ['direct-applics', 'indirect-applics', 'int-applics'])
    unit.set_prop('worth', 338)

    # arity
    unit = registry.create_unit('arity')
    unit.set_prop('data-type', NUMBER)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # best-choose
    unit = registry.create_unit('best-choose')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', best_choose)
    unit.set_prop('generalizations', ['random-choose', 'good-choose'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'set-op', 'anything', 'struc-op', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('worth', 500)

    # best-subset
    unit = registry.create_unit('best-subset')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', best_subset)
    unit.set_prop('generalizations', ['random-subset', 'good-subset'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'set-op', 'anything', 'struc-op', 'unary-op'])
    unit.set_prop('range', ['set'])
    unit.set_prop('rarity', [0.95, 19, 1])
    unit.set_prop('worth', 500)

    # bit
    unit = registry.create_unit('bit')
    unit.set_prop('examples', [True, []])
    unit.set_prop('fast-defn', lambda b: not b or b is True)
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('is-range-of', ['equal', 'ieqp', 'eq', 'ileq', 'igeq', 'ilessp', 'igreaterp', 'struc-equal', 'set-equal', 'subsetp', 'always-t', 'always-nil', 'constant-binary-pred', 'always-t-2', 'always-nil-2', 'constant-unary-pred', 'o-set-equal', 'bag-equal', 'list-equal', 'member', 'memb', 'not'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # category
    unit = registry.create_unit('category')
    unit.set_prop('examples', ['set', 'heuristic', 'anything', 'math-concept', 'slot', 'math-obj', 'nnumber', 'unit', 'prime-num', 'conjecture', 'repr-concept', 'even-num', 'task', 'math-op', 'odd-num', 'perf-num', 'perf-square', 'op', 'set-of-numbers', 'set-op', 'unit-op', 'num-op', 'criterial-slot', 'pred', 'math-pred', 'bit', 'non-criterial-slot', 'hind-sight-rule', 'unary-unit-op', 'record-slot', 'structure', 'category', 'constant-pred', 'struc-op', 'list-op', 'list', 'bag', 'bag-op', 'mult-ele-struc', 'mult-ele-struc-op', 'o-set', 'o-set-op', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc', 'ord-struc-op', 'type-of-structure', 'unary-op', 'binary-op', 'tertiary-op', 'o-pair', 'pair', 'inverted-op', 'set-of-o-pairs', 'relation', 'logic-op', 'atom', 'truth-value', 'structure-of-structures', 'set-of-sets', 'empty-struc', 'non-empty-struc', 'unary-pred', 'binary-pred', 'tertiary-pred', 'pred-cat-by-nargs', 'op-cat-by-nargs'])
    unit.set_prop('interestingness', ['interp3', Quoted(Symbol('h24')), 'u', Quoted(Symbol('why-int'))])
    unit.set_prop('isa', ['category', 'anything', 'repr-concept'])
    unit.set_prop('specializations', ['type-of-structure', 'pred-cat-by-nargs', 'op-cat-by-nargs'])
    unit.set_prop('worth', 500)

    # compiled-defn
    unit = registry.create_unit('compiled-defn')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['defn'])
    unit.set_prop('worth', 600)

    # compose
    unit = registry.create_unit('compose')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['op', 'op'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', TODO("(lambda (f g) (cond ((and (range f) (domain g) (is-a-kind-of (car (range f)) (car (domain g)))) (let ((fargs (mapcar \\#\\'the-second-of (domain f) '(u v w x y z z2 z3 z4 z5))) (gargs (mapcar \\#\\'the-second-of (cdr (domain g)) '(a b c d e f g h i j k))) (nam (create-unit (pack* g '-o- f)))) (put nam 'isa (set-diff (isa g) (examples 'op-cat-by-nargs))) (put nam 'worth (average-worths 'compose (average-worths f g))) (put nam 'arity (+ (length fargs) (length gargs))) (put nam 'domain (append (copy (domain f)) (cdr (domain g)))) (put nam 'range (copy (range g))) (put nam 'unitized-alg (compile-report \\` (lambda \\, (nconc (copy fargs) (copy gargs)) (run-alg '\\,g (run-alg '\\,f \\,@fargs) \\,@gargs)))) (put nam 'elim-slots '(applics)) (put nam 'creditors '(compose)) (put nam 'isa (append (isa nam) (subset (examples 'op-cat-by-nargs) (lambda (pc) (run-defn pc nam))))) (add-inv nam) nam)) (t 'failed)))"))
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'anything', 'binary-op'])
    unit.set_prop('range', ['op'])
    unit.set_prop('rarity', [0.3612903, 56, 99])
    unit.set_prop('worth', 990)

    # conjecture
    unit = registry.create_unit('conjecture')
    unit.set_prop('examples', ['proto-conjec'])
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # conjecture-about
    unit = registry.create_unit('conjecture-about')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['conjectures'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # conjectures
    unit = registry.create_unit('conjectures')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['conjecture-about'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # constant-binary-pred
    unit = registry.create_unit('constant-binary-pred')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['op', 'pred', 'anything', 'unary-op', 'math-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('specializations', ['always-t-2', 'always-nil-2'])
    unit.set_prop('worth', 500)

    # constant-pred
    unit = registry.create_unit('constant-pred')
    unit.set_prop('examples', ['always-t', 'always-nil', 'always-t-2', 'always-nil-2'])
    unit.set_prop('generalizations', ['op', 'pred', 'anything'])
    unit.set_prop('isa', ['anything', 'category', 'math-op', 'repr-concept'])
    unit.set_prop('worth', 500)

    # constant-unary-pred
    unit = registry.create_unit('constant-unary-pred')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['op', 'pred', 'anything', 'unary-op', 'math-op', 'unary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('specializations', ['always-t', 'always-nil'])
    unit.set_prop('worth', 500)

    # creditors
    unit = registry.create_unit('creditors')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('to-delete-1', ['lambda', ['u1', 'p', 'u2'], ['declare', ['ignore', 'p']], ['rem1prop', 'u1', Quoted(Symbol('applics')), ['find-if', ['lambda', ['a'], ['eq', ['caadr', 'a'], 'u2']], ['applics', 'u1']]]])
    unit.set_prop('worth', 300)

    # criterial-slot
    unit = registry.create_unit('criterial-slot')
    unit.set_prop('examples', ['alg', 'applic-generator', 'compiled-defn', 'data-type', 'defn', 'domain', 'elim-slots', 'fast-alg', 'fast-defn', 'generator', 'if-about-to-work-on-task', 'if-finished-working-on-task', 'if-parts', 'if-potentially-relevant', 'if-task-parts', 'if-truly-relevant', 'if-working-on-task', 'iterative-alg', 'iterative-defn', 'non-examples', 'recursive-alg', 'recursive-defn', 'then-add-to-agenda', 'then-compute', 'then-conjecture', 'then-define-new-concepts', 'then-modify-slots', 'then-parts', 'then-print-to-user', 'to-delete', 'to-delete-1', 'unitized-alg', 'unitized-defn', 'then-delete-old-concepts', 'nec-defn', 'suf-defn', 'each-element-is-a'])
    unit.set_prop('generalizations', ['slot', 'anything', 'repr-concept'])
    unit.set_prop('isa', ['repr-concept', 'math-concept', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # data-type
    unit = registry.create_unit('data-type')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # defn
    unit = registry.create_unit('defn')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('specializations', ['nec-defn', 'suf-defn'])
    unit.set_prop('sub-slots', ['compiled-defn', 'fast-defn', 'iterative-defn', 'recursive-defn', 'unitized-defn', 'suf-defn', 'nec-defn'])
    unit.set_prop('worth', 600)

    # direct-applics
    unit = registry.create_unit('direct-applics')
    unit.set_prop('data-type', IO_PAIR)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('format', [['situation', 'resultant-units', 'directness'], ['situation', 'resultant-units', 'directness'], 'etc.'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['applics'])
    unit.set_prop('worth', 300)

    # divisors-of
    unit = registry.create_unit('divisors-of')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', TODO("(lambda (n) (sort (loop for i from 1 until (> (square i) n) when (divides i n) collect i and collect (floor n i)) \\#\\'<))"))
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'num-op', 'anything', 'unary-op'])
    unit.set_prop('iterative-alg', lambda n: [i for i in range(1, n+1) if divides(i, n)])
    unit.set_prop('range', ['set-of-numbers'])
    unit.set_prop('worth', 500)

    # domain
    unit = registry.create_unit('domain')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('inverse', ['in-domain-of'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # dont-copy
    unit = registry.create_unit('dont-copy')
    unit.set_prop('data-type', BIT)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # double-check
    unit = registry.create_unit('double-check')
    unit.set_prop('data-type', BIT)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # eq
    unit = registry.create_unit('eq')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', eq)
    unit.set_prop('generalizations', ['equal'])
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.1, 1, 9])
    unit.set_prop('worth', 507)

    # equal
    unit = registry.create_unit('equal')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', equals)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('specializations', ['ieqp', 'eq', 'struc-equal', 'set-equal', 'o-set-equal', 'bag-equal', 'list-equal'])
    unit.set_prop('worth', 502)

    # elim-slots
    unit = registry.create_unit('elim-slots')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # english
    unit = registry.create_unit('english')
    unit.set_prop('data-type', STRING)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 304)

    # even-num
    unit = registry.create_unit('even-num')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', lambda n: fixp(n) and divides(2, n))
    unit.set_prop('generalizations', ['nnumber', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('unitized-defn', TODO("(lambda (n) (run-alg 'divides 2 n))"))
    unit.set_prop('worth', 800)

    # examples
    unit = registry.create_unit('examples')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['isa'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('more-interesting', ['int-examples'])
    unit.set_prop('sub-slots', ['int-examples'])
    unit.set_prop('worth', 300)

    # failed-record
    unit = registry.create_unit('failed-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['failed-record-for'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # failed-record-for
    unit = registry.create_unit('failed-record-for')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['failed-record'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # fast-alg
    unit = registry.create_unit('fast-alg')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['alg'])
    unit.set_prop('worth', 600)

    # fast-defn
    unit = registry.create_unit('fast-defn')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['defn'])
    unit.set_prop('worth', 600)

    # format
    unit = registry.create_unit('format')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 400)

    # generalizations
    unit = registry.create_unit('generalizations')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['specializations'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('sub-slots', ['super-slots', 'extensions'])
    unit.set_prop('worth', 306)

    # generator
    unit = registry.create_unit('generator')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('format', ['gen-init', 'gen-build', 'gen-args'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # good-choose
    unit = registry.create_unit('good-choose')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', good_choose)
    unit.set_prop('generalizations', ['random-choose'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'set-op', 'anything', 'struc-op', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['best-choose'])
    unit.set_prop('worth', 500)

    # good-subset
    unit = registry.create_unit('good-subset')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', good_subset)
    unit.set_prop('generalizations', ['random-subset'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'set-op', 'anything', 'struc-op', 'unary-op'])
    unit.set_prop('range', ['set'])
    unit.set_prop('specializations', ['best-subset'])
    unit.set_prop('worth', 500)

    # heuristic
    unit = registry.create_unit('heuristic')
    unit.set_prop('examples', ['h1', 'h5', 'h6', 'h3', 'h4', 'h7', 'h8', 'h9', 'h10', 'h11', 'h2', 'h12', 'h-avoid', 'h-avoid-2', 'h-avoid-3', 'h13', 'h14', 'h15', 'h16', 'h17', 'h18', 'h19', 'h-avoid-2-and', 'h-avoid-3-first', 'h-avoid-if-working', 'h5-criterial', 'h5-good', 'h19-criterial', 'h20', 'h21', 'h22', 'h23', 'h24', 'h25', 'h26', 'h27', 'h28', 'h20', '#|h1-6|#'])
    unit.set_prop('generalizations', ['op', 'anything', 'repr-concept'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('specializations', ['hind-sight-rule'])
    unit.set_prop('worth', 900)

    # hind-sight-rule
    unit = registry.create_unit('hind-sight-rule')
    unit.set_prop('abbrev', ['Heuristic rules for learning from bitter experiences'])
    unit.set_prop('examples', ['h12', 'h13', 'h14'])
    unit.set_prop('generalizations', ['op', 'heuristic', 'anything', 'repr-concept'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('worth', 900)

    # ieqp
    unit = registry.create_unit('ieqp')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['nnumber', 'nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', equals_num)
    unit.set_prop('generalizations', ['equal', 'ileq', 'igeq'])
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'num-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.1, 1, 9])
    unit.set_prop('worth', 500)

    # igeq
    unit = registry.create_unit('igeq')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['nnumber', 'nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', greater_equal)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'num-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('specializations', ['ieqp', 'igreaterp'])
    unit.set_prop('transpose', ['ileq'])
    unit.set_prop('worth', 509)

    # igreaterp
    unit = registry.create_unit('igreaterp')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['nnumber', 'nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', greater)
    unit.set_prop('generalizations', ['igeq'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'num-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('transpose', ['ilessp'])
    unit.set_prop('worth', 501)

    # ileq
    unit = registry.create_unit('ileq')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['nnumber', 'nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', less_equal)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'num-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('specializations', ['ieqp', 'ilessp'])
    unit.set_prop('transpose', ['igeq'])
    unit.set_prop('worth', 500)

    # ilessp
    unit = registry.create_unit('ilessp')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['nnumber', 'nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', less)
    unit.set_prop('generalizations', ['ileq'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'num-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('transpose', ['igreaterp'])
    unit.set_prop('worth', 500)

    # if-about-to-work-on-task
    unit = registry.create_unit('if-about-to-work-on-task')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['if-parts', 'if-task-parts'])
    unit.set_prop('worth', 600)

    # if-finished-working-on-task
    unit = registry.create_unit('if-finished-working-on-task')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['if-task-parts', 'if-parts'])
    unit.set_prop('worth', 600)

    # if-parts
    unit = registry.create_unit('if-parts')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('sub-slots', ['if-potentially-relevant', 'if-truly-relevant', 'if-about-to-work-on-task', 'if-working-on-task', 'if-finished-working-on-task'])
    unit.set_prop('worth', 600)

    # if-potentially-relevant
    unit = registry.create_unit('if-potentially-relevant')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['if-parts'])
    unit.set_prop('worth', 600)

    # if-task-parts
    unit = registry.create_unit('if-task-parts')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('sub-slots', ['if-about-to-work-on-task', 'if-working-on-task', 'if-finished-working-on-task'])
    unit.set_prop('worth', 600)

    # if-truly-relevant
    unit = registry.create_unit('if-truly-relevant')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['if-parts'])
    unit.set_prop('worth', 600)

    # if-working-on-task
    unit = registry.create_unit('if-working-on-task')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['if-parts', 'if-task-parts'])
    unit.set_prop('worth', 600)

    # in-domain-of
    unit = registry.create_unit('in-domain-of')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('inverse', ['domain'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # indirect-applics
    unit = registry.create_unit('indirect-applics')
    unit.set_prop('data-type', IO_PAIR)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('format', [['situation', 'resultant-units', 'directness'], ['situation', 'resultant-units', 'directness'], 'etc.'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['applics'])
    unit.set_prop('worth', 300)

    # inverse
    unit = registry.create_unit('inverse')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['inverse'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # isa
    unit = registry.create_unit('isa')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['examples'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # is-range-of
    unit = registry.create_unit('is-range-of')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('inverse', ['range'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # iterative-alg
    unit = registry.create_unit('iterative-alg')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['alg'])
    unit.set_prop('worth', 600)

    # iterative-defn
    unit = registry.create_unit('iterative-defn')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['defn'])
    unit.set_prop('worth', 600)

    # math-concept
    unit = registry.create_unit('math-concept')
    unit.set_prop('examples', ['nnumber', 'prime-num', 'perf-num', 'perf-square', 'odd-num', 'even-num', 'square', 'divisors-of', 'multiply', 'add', 'successor', 'set', 'set-of-numbers', 'random-choose', 'random-subset', 'good-choose', 'best-choose', 'best-subset', 'good-subset', 'bit', 'equal', 'ieqp', 'eq', 'ileq', 'igeq', 'ilessp', 'igreaterp', 'slot', 'unit', 'criterial-slot', 'non-criterial-slot', 'math-concept', 'math-obj', 'math-op', 'math-pred', 'num-op', 'set-op', 'los1', 'los2', 'los3', 'los4', 'los5', 'los6', 'los7', 'win1', 'record-slot', 'structure', 'struc-equal', 'set-equal', 'subsetp', 'compose', 'struc-insert', 'struc-op', 'struc-delete', 'set-insert', 'set-delete', 'list-op', 'list', 'list-insert', 'list-delete', 'list-delete-1', 'bag', 'bag-op', 'bag-insert', 'bag-delete', 'bag-delete-1', 'mult-ele-struc', 'mult-ele-struc-op', 'mult-ele-struc-delete-1', 'o-set', 'o-set-insert', 'o-set-op', 'o-set-delete', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc', 'o-set-equal', 'bag-equal', 'list-equal', 'ord-struc-op', 'ord-struc-equal', 'set-intersect', 'set-union', 'struc-intersect', 'list-intersect', 'o-set-intersect', 'bag-intersect', 'struc-union', 'o-set-union', 'list-union', 'bag-union', 'struc-difference', 'set-difference', 'list-difference', 'o-set-difference', 'bag-difference', 'coalesce', 'parallel-replace', 'parallel-replace-2', 'repeat', 'repeat2', 'parallel-join', 'parallel-join-2', 'o-pair', 'pair', 'reverse-o-pair', 'first-ele', 'second-ele', 'third-ele', 'all-but-first', 'all-but-second', 'all-but-third', 'last-ele', 'all-but-last', 'member', 'memb', 'proj1', 'proj2', 'proj-1-of-3', 'proj-2-of-3', 'proj-3-of-3', 'identity-1', 'restrict', 'inverted-op', 'invert-op', 'set-of-o-pairs', 'relation', 'logic-op', 'structure-of-structures', 'set-of-sets', 'empty-struc', 'non-empty-struc', 'mult-ele-struc-insert', 'restrict-random-subset-3'])
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['math-op', 'math-obj', 'set-op', 'unit-op', 'num-op', 'math-pred', 'struc-op', 'list-op', 'bag-op', 'mult-ele-struc-op', 'o-set-op', 'ord-struc-op', 'inverted-op', 'logic-op'])
    unit.set_prop('worth', 500)

    # math-obj
    unit = registry.create_unit('math-obj')
    unit.set_prop('examples', ['nnumber', 'prime-num', 'perf-num', 'perf-square', 'odd-num', 'even-num', 'set', 'set-of-numbers', 'bit', 'math-concept', 'num-op', 'set-op', 'math-pred', 'math-obj', 'math-op', 'los1', 'los2', 'los3', 'los4', 'los5', 'los6', 'los7', 'win1', 'structure', 'struc-op', 'list-op', 'list', 'bag', 'bag-op', 'mult-ele-struc', 'mult-ele-struc-op', 'o-set', 'o-set-op', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc', 'ord-struc-op', 'o-pair', 'pair', 'inverted-op', 'set-of-o-pairs', 'relation', 'logic-op', 'structure-of-structures', 'set-of-sets', 'empty-struc', 'non-empty-struc', 'truth-value'])
    unit.set_prop('generalizations', ['math-concept', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # math-op
    unit = registry.create_unit('math-op')
    unit.set_prop('examples', ['divisors-of', 'square', 'multiply', 'add', 'successor', 'random-choose', 'random-subset', 'good-choose', 'best-choose', 'best-subset', 'good-subset', 'equal', 'ieqp', 'eq', 'ileq', 'igeq', 'ilessp', 'igreaterp', 'and', 'or', 'the-first-of', 'the-second-of', 'struc-equal', 'set-equal', 'subsetp', 'compose', 'struc-insert', 'struc-delete', 'set-insert', 'set-delete', 'list-insert', 'list-delete', 'list-delete-1', 'bag-insert', 'bag-delete', 'bag-delete-1', 'mult-ele-struc-delete-1', 'o-set-insert', 'o-set-delete', 'o-set-equal', 'bag-equal', 'list-equal', 'ord-struc-equal', 'set-intersect', 'set-union', 'struc-intersect', 'list-intersect', 'o-set-intersect', 'bag-intersect', 'struc-union', 'o-set-union', 'list-union', 'bag-union', 'struc-difference', 'set-difference', 'list-difference', 'o-set-difference', 'bag-difference', 'coalesce', 'parallel-replace', 'parallel-replace-2', 'repeat', 'repeat2', 'parallel-join', 'parallel-join-2', 'reverse-o-pair', 'first-ele', 'second-ele', 'third-ele', 'all-but-first', 'all-but-second', 'all-but-third', 'last-ele', 'all-but-last', 'member', 'memb', 'proj1', 'proj2', 'proj-1-of-3', 'proj-2-of-3', 'proj-3-of-3', 'identity-1', 'restrict', 'invert-op', 'not', 'implies', 'always-nil', 'always-nil-2', 'always-t', 'always-t-2', 'constant-binary-pred', 'constant-pred', 'constant-unary-pred', 'undefined-pred', 'mult-ele-struc-insert', 'restrict-random-subset-3'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['set-op', 'unit-op', 'num-op', 'struc-op', 'list-op', 'bag-op', 'mult-ele-struc-op', 'o-set-op', 'ord-struc-op', 'inverted-op', 'logic-op'])
    unit.set_prop('worth', 500)

    # math-pred
    unit = registry.create_unit('math-pred')
    unit.set_prop('examples', ['equal', 'ieqp', 'eq', 'ileq', 'igeq', 'ilessp', 'igreaterp', 'and', 'or', 'the-first-of', 'the-second-of', 'struc-equal', 'set-equal', 'subsetp', 'o-set-equal', 'bag-equal', 'list-equal', 'member', 'memb', 'not', 'implies'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'pred', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # multiply
    unit = registry.create_unit('multiply')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['nnumber', 'nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: x * y)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'num-op', 'anything', 'binary-op'])
    unit.set_prop('iterative-alg', lambda x, y: x * y)
    unit.set_prop('range', ['nnumber'])
    unit.set_prop('recursive-alg', TODO("(lambda (x y) (cond ((eq x 0) 0) ((eq x 1) y) (t (run-alg 'add y (run-alg 'multiply (1- x) y)))))"))
    unit.set_prop('unitized-alg', TODO("(lambda (x y) (cond ((eq x 0) 0) ((eq x 1) y) (t (run-alg 'add y (run-alg 'multiply (1- x) y)))))"))
    unit.set_prop('worth', 500)

    # nnumber
    unit = registry.create_unit('nnumber')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', fixp)
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('generator', [[0], ['1+'], ['old']])
    unit.set_prop('in-domain-of', ['divisors-of', 'multiply', 'add', 'successor', 'square', 'ieqp', 'ileq', 'igeq', 'ilessp', 'igreaterp'])
    unit.set_prop('is-range-of', ['multiply', 'add', 'successor'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('rarity', [0, 1, 3])
    unit.set_prop('specializations', ['prime-num', 'perf-num', 'perf-square', 'odd-num', 'even-num'])
    unit.set_prop('worth', 500)

    # non-criterial-slot
    unit = registry.create_unit('non-criterial-slot')
    unit.set_prop('examples', ['abbrev', 'applics', 'arity', 'creditors', 'direct-applics', 'dont-copy', 'double-check', 'english', 'examples', 'format', 'generalizations', 'in-domain-of', 'indirect-applics', 'isa', 'is-range-of', 'range', 'sib-slots', 'specializations', 'sub-slots', 'super-slots', 'transpose', 'worth', 'inverse', 'subsumes', 'subsumed-by', 'overall-record', 'then-print-to-user-failed-record', 'then-add-to-agenda-failed-record', 'then-delete-old-concepts-failed-record', 'then-define-new-concepts-failed-record', 'then-conjecture-failed-record', 'then-modify-slots-failed-record', 'then-compute-failed-record', 'then-print-to-user-record', 'then-add-to-agenda-record', 'then-delete-old-concepts-record', 'then-define-new-concepts-record', 'then-conjecture-record', 'then-modify-slots-record', 'then-compute-record', 'record-for', 'failed-record-for', 'record', 'failed-record', 'conjectures', 'conjecture-about', 'lower-arity', 'higher-arity', 'extensions', 'restrictions', 'interestingness', 'more-interesting', 'less-interesting', 'int-examples', 'why-int', 'rarity', 'is-a-int', 'int-applics'])
    unit.set_prop('generalizations', ['slot', 'anything', 'repr-concept'])
    unit.set_prop('isa', ['repr-concept', 'math-concept', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # non-examples
    unit = registry.create_unit('non-examples')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('double-check', True)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # num-op
    unit = registry.create_unit('num-op')
    unit.set_prop('abbrev', ['Numeric Operations'])
    unit.set_prop('examples', ['divisors-of', 'square', 'multiply', 'add', 'successor', 'ieqp', 'ileq', 'igeq', 'ilessp', 'igreaterp'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # or
    unit = registry.create_unit('or')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: x or y)
    unit.set_prop('isa', ['op', 'pred', 'math-op', 'math-pred', 'anything', 'binary-op', 'logic-op', 'binary-pred'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['the-first-of', 'the-second-of', 'and'])
    unit.set_prop('worth', 500)

    # odd-num
    unit = registry.create_unit('odd-num')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', lambda n: fixp(n) and oddp(n))
    unit.set_prop('generalizations', ['nnumber', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('unitized-defn', TODO("(lambda (n) (not (run-alg 'divides 2 n)))"))
    unit.set_prop('worth', 700)

    # op
    unit = registry.create_unit('op')
    unit.set_prop('examples', ['random-choose', 'random-subset', 'good-choose-best-choose', 'best-subset', 'good-subset', 'divisors-of', 'square', 'multiply', 'add', 'successor', 'equal', 'ieqp', 'eq', 'ileq', 'igeq', 'ilessp', 'igreaterp', 'h12', 'h13', 'h14', 'h1', 'h5', 'h6', 'h3', 'h4', 'h7', 'h8', 'h9', 'h10', 'h11', 'h2', 'h-avoid', 'h-avoid-2', 'h-avoid-3', 'h15', 'and', 'or', 'the-second-of', 'the-first-of', 'h19', 'h-avoid-2-and', 'h-avoid-3-first', 'h-avoid-if-working', 'h5-criterial', 'h5-good', 'h19-criterial', 'h20', 'h21', 'struc-equal', 'set-equal', 'subsetp', 'always-t', 'always-nil', 'constant-binary-pred', 'always-t-2', 'always-nil-2', 'constant-unary-pred', 'compose', 'undefined-pred', 'struc-insert', 'struc-delete', 'set-insert', 'set-delete', 'list-insert', 'list-delete', 'list-delete-1', 'bag-insert', 'bag-delete', 'bag-delete-1', 'mult-ele-struc-delete-1', 'o-set-insert', 'o-set-delete', 'o-set-equal', 'bag-equal', 'list-equal', 'ord-struc-equal', 'set-intersect', 'set-union', 'struc-intersect', 'list-intersect', 'o-set-intersect', 'bag-intersect', 'struc-union', 'o-set-union', 'list-union', 'bag-union', 'struc-difference', 'set-difference', 'list-difference', 'o-set-difference', 'bag-difference', 'coalesce', 'parallel-replace', 'parallel-replace-2', 'repeat', 'repeat2', 'parallel-join', 'parallel-join-2', 'reverse-o-pair', 'first-ele', 'second-ele', 'third-ele', 'all-but-first', 'all-but-second', 'all-but-third', 'last-ele', 'all-but-last', 'member', 'memb', 'proj1', 'proj2', 'proj-1-of-3', 'proj-2-of-3', 'proj-3-of-3', 'identity-1', 'restrict', 'invert-op', 'not', 'implies', 'h22', 'h23', 'h24', 'h29', 'h16', 'h17', 'h18', 'h25', 'h26', 'h27', 'h28', 'mult-ele-struc-insert', '#|h1-6|#'])
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('in-domain-of', ['compose', 'coalesce', 'restrict', 'invert-op'])
    unit.set_prop('is-range-of', ['compose', 'coalesce', 'restrict'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('specializations', ['math-op', 'heuristic', 'set-op', 'unit-op', 'num-op', 'pred', 'math-pred', 'hind-sight-rule', 'constant-pred', 'struc-op', 'list-op', 'bag-op', 'mult-ele-struc-op', 'o-set-op', 'ord-struc-op', 'unary-op', 'binary-op', 'tertiary-op', 'inverted-op', 'logic-op', 'unary-pred', 'binary-pred', 'tertiary-pred'])
    unit.set_prop('worth', 500)

    # overall-record
    unit = registry.create_unit('overall-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything', 'record-slot'])
    unit.set_prop('worth', 300)

    # perf-num
    unit = registry.create_unit('perf-num')
    unit.set_prop('elim-slots', [])
    unit.set_prop('examples', [6, 28])
    unit.set_prop('generalizations', ['nnumber', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('iterative-defn', lambda n: fixp(n) and n-1 == sum(i for i in range(2, n) if divides(i, n)))
    unit.set_prop('non-examples', [0, 1])
    unit.set_prop('unitized-defn', TODO("(lambda (n) (eq (run-alg 'double n) (apply \\#\\'+ (run-alg 'divisors-of n))))"))
    unit.set_prop('worth', 800)

    # perf-square
    unit = registry.create_unit('perf-square')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('generalizations', ['nnumber', 'anything'])
    unit.set_prop('is-range-of', ['square'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('worth', 950)

    # pred
    unit = registry.create_unit('pred')
    unit.set_prop('abbrev', ['Boolean predicates'])
    unit.set_prop('examples', ['equal', 'ieqp', 'eq', 'ileq', 'igeq', 'ilessp', 'igreaterp', 'and', 'or', 'the-second-of', 'the-first-of', 'struc-equal', 'set-equal', 'subsetp', 'always-t', 'always-nil', 'constant-binary-pred', 'always-t-2', 'always-nil-2', 'constant-unary-pred', 'undefined-pred', 'o-set-equal', 'bag-equal', 'list-equal', 'member', 'memb', 'not', 'implies'])
    unit.set_prop('generalizations', ['op', 'anything'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('specializations', ['math-pred', 'constant-pred', 'unary-pred', 'binary-pred', 'tertiary-pred'])
    unit.set_prop('worth', 500)

    # prime-num
    unit = registry.create_unit('prime-num')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', lambda n: fixp(n) and all(not divides(i, n) for i in range(2, int(n ** 0.5) + 1)))
    unit.set_prop('generalizations', ['nnumber', 'anything'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('iterative-defn', lambda n: fixp(n) and 0 == sum(i for i in range(2, n) if divides(i, n)))
    unit.set_prop('non-examples', [0, 1])
    unit.set_prop('unitized-defn', TODO("(lambda (n) (run-defn (run-alg 'divisors-of n) 'doubleton))"))
    unit.set_prop('worth', 950)

    # proto-conjec
    unit = registry.create_unit('proto-conjec')
    unit.set_prop('isa', ['conjecture', 'repr-concept', 'anything'])
    unit.set_prop('worth', 802)

    # random-choose
    unit = registry.create_unit('random-choose')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', random_choose)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'set-op', 'anything', 'struc-op', 'unary-op'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['good-choose', 'best-choose'])
    unit.set_prop('worth', 507)

    # random-subset
    unit = registry.create_unit('random-subset')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', random_subset)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'set-op', 'anything', 'struc-op', 'unary-op'])
    unit.set_prop('range', ['set'])
    unit.set_prop('rarity', [0.4065041, 50, 73])
    unit.set_prop('specializations', ['best-subset', 'good-subset'])
    unit.set_prop('worth', 520)

    # range
    unit = registry.create_unit('range')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('inverse', ['is-range-of'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # record
    unit = registry.create_unit('record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['record-for'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # record-for
    unit = registry.create_unit('record-for')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['record'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # record-slot
    unit = registry.create_unit('record-slot')
    unit.set_prop('examples', ['then-compute-record', 'then-compute-failed-record', 'then-modify-slots-record', 'then-modify-slots-failed-record', 'then-conjecture-record', 'then-conjecture-failed-record', 'then-define-new-concepts-record', 'then-define-new-concepts-failed-record', 'then-delete-old-concepts-record', 'then-delete-old-concepts-failed-record', 'then-add-to-agenda-record', 'then-add-to-agenda-failed-record', 'then-print-to-user-record', 'then-print-to-user-failed-record', 'overall-record'])
    unit.set_prop('generalizations', ['slot', 'anything', 'repr-concept'])
    unit.set_prop('isa', ['repr-concept', 'math-concept', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # recursive-alg
    unit = registry.create_unit('recursive-alg')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['alg'])
    unit.set_prop('worth', 600)

    # recursive-defn
    unit = registry.create_unit('recursive-defn')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['defn'])
    unit.set_prop('worth', 600)

    # repr-concept
    unit = registry.create_unit('repr-concept')
    unit.set_prop('examples', ['slot', 'unit', 'criterial-slot', 'non-criterial-slot', 'heuristic', 'hind-sight-rule', 'unit-op', 'unary-unit-op', 'repr-concept', 'conjecture', 'task', 'anything', 'pred', 'op', 'proto-conjec', 'abbrev', 'alg', 'applic-generator', 'applics', 'arity', 'compiled-defn', 'creditors', 'data-type', 'defn', 'direct-applics', 'domain', 'dont-copy', 'double-check', 'elim-slots', 'english', 'examples', 'failed-record', 'failed-record-for', 'fast-alg', 'fast-defn', 'format', 'generalizations', 'generator', 'if-about-to-work-on-task', 'if-finished-working-on-task', 'if-parts', 'if-potentially-relevant', 'if-task-parts', 'if-truly-relevant', 'if-working-on-task', 'in-domain-of', 'indirect-applics', 'inverse', 'isa', 'is-range-of', 'iterative-alg', 'iterative-defn', 'non-examples', 'overall-record', 'range', 'record', 'record-for', 'recursive-alg', 'recursive-defn', 'sib-slots', 'specializations', 'sub-slots', 'subsumed-by', 'subsumes', 'super-slots', 'then-add-to-agenda', 'then-add-to-agenda-failed-record', 'then-add-to-agenda-record', 'then-compute', 'then-compute-failed-record', 'then-compute-record', 'then-conjecture', 'then-conjecture-failed-record', 'then-conjecture-record', 'then-define-new-concepts', 'then-define-new-concepts-failed-record', 'then-define-new-concepts-record', 'then-delete-old-concepts', 'then-delete-old-concepts-failed-record', 'then-delete-old-concepts-record', 'then-modify-slots', 'then-modify-slots-failed-record', 'then-modify-slots-record', 'then-parts', 'then-print-to-user', 'then-print-to-user-failed-record', 'then-print-to-user-record', 'to-delete', 'to-delete-1', 'transpose', 'unitized-alg', 'unitized-defn', 'worth', 'record-slot', 'conjectures', 'conjecture-about', 'category', 'nec-defn', 'suf-defn', 'type-of-structure', 'unary-op', 'each-element-is-a', 'binary-op', 'tertiary-op', 'atom', 'constant-pred', 'undefined', 'lower-arity', 'higher-arity', 'unary-pred', 'binary-pred', 'tertiary-pred', 'pred-cat-by-nargs', 'op-cat-by-nargs', 'extensions', 'restrictions', 'interestingness', 'more-interesting', 'less-interesting', 'int-examples', 'why-int', 'rarity', 'is-a-int', 'int-applics', 'english-1'])
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('specializations', ['slot', 'criterial-slot', 'non-criterial-slot', 'unit', 'heuristic', 'hind-sight-rule', 'record-slot'])
    unit.set_prop('worth', 500)

    # set
    unit = registry.create_unit('set')
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', lambda s: not s or no_repeats_in(s))
    unit.set_prop('generalizations', ['anything', 'structure', 'bag', 'list', 'no-mult-ele-struc', 'un-ord-struc'])
    unit.set_prop('generator', [[[]], ['get-a-set'], ['old']])
    unit.set_prop('in-domain-of', ['random-choose', 'random-subset', 'good-choose', 'best-choose', 'best-subset', 'good-subset', 'set-equal', 'subsetp', 'set-insert', 'set-delete', 'set-intersect', 'set-union', 'set-difference'])
    unit.set_prop('is-range-of', ['random-subset', 'best-subset', 'good-subset', 'set-insert', 'set-delete', 'set-intersect', 'set-union', 'set-difference', 'restrict-random-subset-2-1', 'restrict-random-subset-1-2'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category', 'type-of-structure'])
    unit.set_prop('rarity', [0, 2, 2])
    unit.set_prop('recursive-defn', TODO("(lambda (s) (cond ((not (consp s)) (eq s ())) (t (and (not (member (car s) (cdr s))) (run-defn 'set (cdr s))))))"))
    unit.set_prop('specializations', ['o-set', 'empty-struc', 'non-empty-struc', 'set-of-sets'])
    unit.set_prop('worth', 500)

    # set-equal
    unit = registry.create_unit('set-equal')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['set', 'set'])
    unit.set_prop('fast-alg', lambda s1, s2: True if len(s1) == len(s2) and equals(s1, s2) else is_subset_of(s1, s2) and is_subset_of(s2, s1))
    unit.set_prop('generalizations', ['equal', 'struc-equal', 'subsetp'])
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'struc-op', 'set-op', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.1, 1, 9])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((and (null s1) (null s2)) t) (t (and (consp s1) (consp s2) (member (car s1) s2) (run-alg 'set-equal (cdr s2) (remove (car s1) s2))))))"))
    unit.set_prop('specializations', ['o-set-equal'])
    unit.set_prop('unitized-alg', TODO("(lambda (s1 s2) (and (run-alg 'subsetp s1 s2) (run-alg 'subsetp s2 s1)))"))
    unit.set_prop('worth', 500)

    # set-of-numbers
    unit = registry.create_unit('set-of-numbers')
    unit.set_prop('each-element-is-a', NUMBER)
    unit.set_prop('elim-slots', ['examples'])
    unit.set_prop('fast-defn', TODO("(lambda (s) (and (run-defn 'set s) (every \\#\\'numberp s)))"))
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('is-range-of', ['divisors-of'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('unitized-defn', TODO("(lambda (s) (and (run-defn 'set s) (every (lambda (n) (run-defn 'nnumber n)) s)))"))
    unit.set_prop('worth', 500)

    # set-op
    unit = registry.create_unit('set-op')
    unit.set_prop('abbrev', ['Set Operations'])
    unit.set_prop('examples', ['random-choose', 'random-subset', 'good-choose', 'best-choose', 'best-subset', 'good-subset', 'set-insert', 'set-delete', 'set-equal', 'set-intersect', 'set-union', 'set-difference'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'anything', 'struc-op'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('specializations', ['unit-op'])
    unit.set_prop('worth', 500)

    # sib-slots
    unit = registry.create_unit('sib-slots')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['sib-slots'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # slot
    unit = registry.create_unit('slot')
    unit.set_prop('examples', ['if-about-to-work-on-task', 'applics', 'if-finished-working-on-task', 'isa', 'if-truly-relevant', 'sub-slots', 'if-parts', 'if-potentially-relevant', 'examples', 'data-type', 'english', 'worth', 'inverse', 'creditors', 'generalizations', 'specializations', 'then-add-to-agenda', 'then-compute', 'then-conjecture', 'abbrev', 'then-define-new-concepts', 'then-modify-slots', 'then-print-to-user', 'then-parts', 'super-slots', 'if-task-parts', 'format', 'dont-copy', 'double-check', 'generator', 'if-working-on-task', 'is-range-of', 'to-delete-1', 'alg', 'fast-defn', 'recursive-defn', 'unitized-defn', 'fast-alg', 'iterative-alg', 'recursive-alg', 'unitized-alg', 'iterative-defn', 'to-delete', 'applic-generator', 'arity', 'non-examples', 'compiled-defn', 'elim-slots', 'in-domain-of', 'domain', 'range', 'indirect-applics', 'direct-applics', 'defn', 'sib-slots', 'transpose', 'then-delete-old-concepts', 'subsumes', 'subsumed-by', 'overall-record', 'then-print-to-user-failed-record', 'then-add-to-agenda-failed-record', 'then-delete-old-concepts-failed-record', 'then-define-new-concepts-failed-record', 'then-conjecture-failed-record', 'then-modify-slots-failed-record', 'then-compute-failed-record', 'then-print-to-user-record', 'then-add-to-agenda-record', 'then-delete-old-concepts-record', 'then-define-new-concepts-record', 'then-conjecture-record', 'then-modify-slots-record', 'then-compute-record', 'record-for', 'failed-record-for', 'record', 'failed-record', 'conjectures', 'conjecture-about', 'nec-defn', 'suf-defn', 'each-element-is-a', 'lower-arity', 'higher-arity', 'extensions', 'restrictions', 'interestingness', 'more-interesting', 'less-interesting', 'int-examples', 'why-int', 'rarity', 'is-a-int', 'int-applics'])
    unit.set_prop('generalizations', ['unary-unit-op', 'repr-concept', 'anything'])
    unit.set_prop('isa', ['repr-concept', 'math-concept', 'anything', 'category'])
    unit.set_prop('specializations', ['criterial-slot', 'non-criterial-slot', 'record-slot'])
    unit.set_prop('worth', 530)

    # specializations
    unit = registry.create_unit('specializations')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['generalizations'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('sub-slots', ['sub-slots', 'restrictions'])
    unit.set_prop('worth', 356)

    # square
    unit = registry.create_unit('square')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda n: n * n)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'num-op', 'anything', 'unary-op'])
    unit.set_prop('range', ['perf-square'])
    unit.set_prop('rarity', [1.0, 220, 0])
    unit.set_prop('unitized-alg', TODO("(lambda (n) (run-alg 'multiply n n))"))
    unit.set_prop('worth', 500)

    # struc-equal
    unit = registry.create_unit('struc-equal')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['structure', 'structure'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('generalizations', ['equal'])
    unit.set_prop('is-a-int', ['binary-pred'])
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('rarity', [0.02, 1, 49])
    unit.set_prop('specializations', ['set-equal', 'o-set-equal', 'bag-equal', 'list-equal'])
    unit.set_prop('worth', 500)

    # structure
    unit = registry.create_unit('structure')
    unit.set_prop('fast-defn', listp)
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('in-domain-of', ['struc-equal', 'struc-insert', 'struc-delete', 'struc-intersect', 'struc-union', 'struc-difference', 'member', 'memb'])
    unit.set_prop('interestingness', ['progn', ['setf', 'u', ['subset', 'u', "#'alivep"]], ['some', ['lambda', ['p'], ['and', ['or', ['has-high-worth', 'p'], ['memb', 'p', ['check-int-examples', Quoted(Symbol('unary-pred'))]]], ['is-rare', 'p'], ['cprin1', 88, 'High worth and rare predicate: ', 'p', '~%'], ['let*', [['tempdef', ['defn', ['car', ['domain', 'p']]]], ['tempu', ['subset', 'u', ['lambda', ['e'], ['failed-to-nil', ['funcall', 'tempdef', 'e']]]]]], ['when', 'tempu', ['let', [['tempdef2', ['subset', 'tempu', ['lambda', ['e'], ['failed-to-nil', ['run-alg', 'p', 'e']]]]]], ['when', 'tempdef2', ['cprin1', 39, 'Potential interesting subset of length: ', ['length', 'tempdef2'], '~%'], ['let', [['temp2', ['find-if', ['lambda', ['p2'], ['failed-to-nil', ['and', ['run-defn', ['cadr', ['domain', 'p2']], 'tempdef2'], ['run-alg', 'p2', 'tempu', 'tempdef2']]]], ['ok-bin-preds', 'tempu']]]], ['when', 'temp2', ['cprin1', 14, '~%The set of elements of size ', ['length', 'u'], ' which satisfy the rare predicate ', 'p', ' form a very special subset; namely, there are in relation ', 'temp2', ' to the entire structure.~%'], ['cprin1', 43, '    They are, by the way: ', 'tempdef2', '~%']]]]]]]]], ['check-examples', Quoted(Symbol('unary-pred'))]]])
    unit.set_prop('is-range-of', ['struc-insert', 'struc-delete', 'struc-intersect', 'struc-union', 'struc-difference'])
    unit.set_prop('isa', ['math-concept', 'math-obj', 'anything', 'category'])
    unit.set_prop('rarity', [0, 2, 2])
    unit.set_prop('recursive-defn', TODO("(lambda (s) (cond ((not (consp s)) (eq s ())) (t (run-defn 'structure (cdr s)))))"))
    unit.set_prop('specializations', ['set', 'list', 'bag', 'mult-ele-struc', 'o-set', 'no-mult-ele-struc', 'ord-struc', 'un-ord-struc', 'o-pair', 'pair', 'empty-struc', 'non-empty-struc'])
    unit.set_prop('worth', 500)

    # sub-slots
    unit = registry.create_unit('sub-slots')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['super-slots'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['specializations'])
    unit.set_prop('worth', 300)

    # subsetp
    unit = registry.create_unit('subsetp')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['set', 'set'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', is_subset_of)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'math-pred', 'pred', 'anything', 'binary-op', 'binary-pred'])
    unit.set_prop('range', ['bit'])
    unit.set_prop('recursive-alg', TODO("(lambda (s1 s2) (cond ((null s1) t) (t (and (consp s1) (member (car s1) s2) (run-alg 'subsetp (cdr s1) s2)))))"))
    unit.set_prop('specializations', ['set-equal', 'o-set-equal'])
    unit.set_prop('worth', 500)

    # subsumed-by
    unit = registry.create_unit('subsumed-by')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['subsumes'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # subsumes
    unit = registry.create_unit('subsumes')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['subsumed-by'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # successor
    unit = registry.create_unit('successor')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['nnumber'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x: x + 1)
    unit.set_prop('isa', ['math-concept', 'math-op', 'op', 'num-op', 'anything', 'unary-op'])
    unit.set_prop('range', ['nnumber'])
    unit.set_prop('worth', 500)

    # super-slots
    unit = registry.create_unit('super-slots')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['sub-slots'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['generalizations'])
    unit.set_prop('worth', 300)

    # task
    unit = registry.create_unit('task')
    unit.set_prop('format', ['priority-value', 'unit-name', 'slot-name', 'reasons', 'misc-args'])
    unit.set_prop('generalizations', ['anything'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # the-first-of
    unit = registry.create_unit('the-first-of')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: x)
    unit.set_prop('generalizations', ['or'])
    unit.set_prop('isa', ['op', 'pred', 'math-op', 'math-pred', 'anything', 'binary-op', 'logic-op', 'binary-pred'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('rarity', [1.0, 42, 0])
    unit.set_prop('specializations', ['and'])
    unit.set_prop('worth', 500)

    # the-second-of
    unit = registry.create_unit('the-second-of')
    unit.set_prop('arity', 2)
    unit.set_prop('domain', ['anything', 'anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('fast-alg', lambda x, y: y)
    unit.set_prop('generalizations', ['or'])
    unit.set_prop('isa', ['op', 'pred', 'math-op', 'math-pred', 'anything', 'binary-op', 'logic-op', 'binary-pred'])
    unit.set_prop('range', ['anything'])
    unit.set_prop('specializations', ['and'])
    unit.set_prop('worth', 500)

    # then-add-to-agenda
    unit = registry.create_unit('then-add-to-agenda')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('failed-record', ['then-add-to-agenda-failed-record'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('record', ['then-add-to-agenda-record'])
    unit.set_prop('super-slots', ['then-parts'])
    unit.set_prop('worth', 600)

    # then-add-to-agenda-failed-record
    unit = registry.create_unit('then-add-to-agenda-failed-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('failed-record-for', ['then-add-to-agenda'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('worth', 300)

    # then-add-to-agenda-record
    unit = registry.create_unit('then-add-to-agenda-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('record-for', ['then-add-to-agenda'])
    unit.set_prop('worth', 300)

    # then-compute
    unit = registry.create_unit('then-compute')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('failed-record', ['then-compute-failed-record'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('record', ['then-compute-record'])
    unit.set_prop('super-slots', ['then-parts'])
    unit.set_prop('worth', 600)

    # then-compute-failed-record
    unit = registry.create_unit('then-compute-failed-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('failed-record-for', ['then-compute'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('worth', 300)

    # then-compute-record
    unit = registry.create_unit('then-compute-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot-non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('record-for', ['then-compute'])
    unit.set_prop('worth', 300)

    # then-conjecture
    unit = registry.create_unit('then-conjecture')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('failed-record', ['then-conjecture-failed-record'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('record', ['then-conjecture-record'])
    unit.set_prop('super-slots', ['then-parts'])
    unit.set_prop('worth', 600)

    # then-conjecture-failed-record
    unit = registry.create_unit('then-conjecture-failed-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('failed-record-for', ['then-conjecture'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('worth', 300)

    # then-conjecture-record
    unit = registry.create_unit('then-conjecture-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('record-for', ['then-conjecture'])
    unit.set_prop('worth', 300)

    # then-define-new-concepts
    unit = registry.create_unit('then-define-new-concepts')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('failed-record', ['then-define-new-concepts-failed-record'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('record', ['then-define-new-concepts-record'])
    unit.set_prop('super-slots', ['then-parts'])
    unit.set_prop('worth', 600)

    # then-define-new-concepts-failed-record
    unit = registry.create_unit('then-define-new-concepts-failed-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('failed-record-for', ['then-define-new-concepts'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('worth', 300)

    # then-define-new-concepts-record
    unit = registry.create_unit('then-define-new-concepts-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('record-for', ['then-define-new-concepts'])
    unit.set_prop('worth', 300)

    # then-delete-old-concepts
    unit = registry.create_unit('then-delete-old-concepts')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('failed-record', ['then-delete-old-concepts-failed-record'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('record', ['then-delete-old-concepts-record'])
    unit.set_prop('super-slots', ['then-parts'])
    unit.set_prop('worth', 600)

    # then-delete-old-concepts-failed-record
    unit = registry.create_unit('then-delete-old-concepts-failed-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('failed-record-for', ['then-delete-old-concepts'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('worth', 300)

    # then-delete-old-concepts-record
    unit = registry.create_unit('then-delete-old-concepts-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('record-for', ['then-delete-old-concepts'])
    unit.set_prop('worth', 300)

    # then-modify-slots
    unit = registry.create_unit('then-modify-slots')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('failed-record', ['then-modify-slots-failed-record'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('record', ['then-modify-slots-record'])
    unit.set_prop('super-slots', ['then-parts'])
    unit.set_prop('worth', 600)

    # then-modify-slots-failed-record
    unit = registry.create_unit('then-modify-slots-failed-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('failed-record-for', ['then-modify-slots'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('worth', 300)

    # then-modify-slots-record
    unit = registry.create_unit('then-modify-slots-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('record-for', ['then-modify-slots'])
    unit.set_prop('worth', 300)

    # then-parts
    unit = registry.create_unit('then-parts')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('sub-slots', ['then-compute', 'then-modify-slots', 'then-conjecture', 'then-define-new-concepts', 'then-delete-old-concepts', 'then-add-to-agenda', 'then-print-to-user'])
    unit.set_prop('worth', 600)

    # then-print-to-user
    unit = registry.create_unit('then-print-to-user')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('failed-record', ['then-print-to-user-failed-record'])
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('record', ['then-print-to-user-record'])
    unit.set_prop('super-slots', ['then-parts'])
    unit.set_prop('worth', 600)

    # then-print-to-user-failed-record
    unit = registry.create_unit('then-print-to-user-failed-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('failed-record-for', ['then-print-to-user'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('worth', 300)

    # then-print-to-user-record
    unit = registry.create_unit('then-print-to-user-record')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('dont-copy', True)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'record-slot', 'anything'])
    unit.set_prop('record-for', ['then-print-to-user'])
    unit.set_prop('worth', 300)

    # to-delete
    unit = registry.create_unit('to-delete')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # to-delete-1
    unit = registry.create_unit('to-delete-1')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 600)

    # transpose
    unit = registry.create_unit('transpose')
    unit.set_prop('data-type', UNIT)
    unit.set_prop('double-check', True)
    unit.set_prop('inverse', ['transpose'])
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 300)

    # unary-unit-op
    unit = registry.create_unit('unary-unit-op')
    unit.set_prop('abbrev', ['Operations performable upon a unit'])
    unit.set_prop('generalizations', ['unit-op', 'anything'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('specializations', ['slot'])
    unit.set_prop('worth', 500)

    # undefined
    unit = registry.create_unit('undefined')
    unit.set_prop('is-range-of', ['undefined-pred'])
    unit.set_prop('isa', ['anything', 'repr-concept'])
    unit.set_prop('worth', 100)

    # undefined-pred
    unit = registry.create_unit('undefined-pred')
    unit.set_prop('arity', 1)
    unit.set_prop('domain', ['anything'])
    unit.set_prop('elim-slots', ['applics'])
    unit.set_prop('isa', ['op', 'pred', 'anything', 'unary-op', 'math-op', 'unary-pred'])
    unit.set_prop('range', ['undefined'])
    unit.set_prop('worth', 100)

    # unit
    unit = registry.create_unit('unit')
    unit.set_prop('generalizations', ['anything', 'repr-concept'])
    unit.set_prop('isa', ['repr-concept', 'math-concept', 'anything', 'category'])
    unit.set_prop('worth', 500)

    # unit-op
    unit = registry.create_unit('unit-op')
    unit.set_prop('abbrev', ['Operations performable upon a set of units'])
    unit.set_prop('generalizations', ['math-concept', 'op', 'math-op', 'set-op', 'anything'])
    unit.set_prop('isa', ['repr-concept', 'anything', 'category'])
    unit.set_prop('specializations', ['unary-unit-op'])
    unit.set_prop('worth', 500)

    # unitized-alg
    unit = registry.create_unit('unitized-alg')
    unit.set_prop('data-type', LISP_FN)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['alg'])
    unit.set_prop('worth', 600)

    # unitized-defn
    unit = registry.create_unit('unitized-defn')
    unit.set_prop('data-type', LISP_PRED)
    unit.set_prop('isa', ['slot', 'criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('super-slots', ['defn'])
    unit.set_prop('worth', 600)

    # worth
    unit = registry.create_unit('worth')
    unit.set_prop('data-type', NUMBER)
    unit.set_prop('isa', ['slot', 'non-criterial-slot', 'repr-concept', 'anything'])
    unit.set_prop('worth', 305)

    # los1
    unit = registry.create_unit('los1')
    unit.set_prop('isa', ['math-obj', 'math-concept', 'anything'])
    unit.set_prop('worth', 100)

    # los2
    unit = registry.create_unit('los2')
    unit.set_prop('isa', ['math-obj', 'math-concept', 'anything'])
    unit.set_prop('worth', 100)

    # los3
    unit = registry.create_unit('los3')
    unit.set_prop('isa', ['math-obj', 'math-concept', 'anything'])
    unit.set_prop('worth', 100)

    # los4
    unit = registry.create_unit('los4')
    unit.set_prop('isa', ['math-obj', 'math-concept', 'anything'])
    unit.set_prop('worth', 100)

    # los5
    unit = registry.create_unit('los5')
    unit.set_prop('isa', ['math-obj', 'math-concept', 'anything'])
    unit.set_prop('worth', 100)

    # los6
    unit = registry.create_unit('los6')
    unit.set_prop('isa', ['math-obj', 'math-concept', 'anything'])
    unit.set_prop('worth', 100)

    # los7
    unit = registry.create_unit('los7')
    unit.set_prop('isa', ['math-obj', 'math-concept', 'anything'])
    unit.set_prop('worth', 100)

    # win1
    unit = registry.create_unit('win1')
    unit.set_prop('isa', ['math-obj', 'math-concept', 'anything'])
    unit.set_prop('worth', 100)
