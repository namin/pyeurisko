"""Convert Eurisko LISP unit definitions to Python format."""

import re
from typing import Dict, List, Any, Tuple, Optional
import sexpdata

def parse_unit_def(e) -> Dict[str, Any]:
    if isinstance(e[0], sexpdata.Symbol) and e[0].value() != 'defunit':
        return None
    name = str(e[1])
    prope = e[2:]
    props = {}
    for i in range(0, len(prope) - 1, 2):
        k = prope[i].value()
        v = prope[i+1]
        if k.startswith('fast'):
            continue
        elif k.endswith('defn'):
            continue
        elif k.endswith('alg'):
            continue
        elif k in ['data-type', 'each-element-is-a']:
            continue
        else:
            props[k] = v
    return {
        'name': name,
        'properties': props
    }

def split_unit_definitions(text: str) -> List[str]:
    """Split a LISP file into individual unit definitions."""
    es = sexpdata.loads("(begin "+text+")")
    units = [parse_unit_def(e) for e in es[1:]]
    units = [u for u in units if u]
    return units

def convert_unit_to_python(unit_data: Dict[str, Any]) -> str:
    """Convert a parsed unit into Python initialization code."""
    name = unit_data['name']
    props = unit_data['properties']
    
    lines = []
    lines.append(f"# {name}")
    lines.append(f"unit = registry.create_unit('{name}')")
    
    for prop, value in sorted(props.items()):
        formatted_value = convert_to_python(value)
        lines.append(f"unit.set_prop('{prop}', {formatted_value})")
    
    lines.append("")  # Add blank line
    return '\n'.join(lines)

def convert_to_python(obj):
    """Recursively convert sexpdata parsed objects into Python native types."""
    if isinstance(obj, sexpdata.Symbol):  # Convert symbols to strings
        return obj.value()
    elif isinstance(obj, list):  # Convert lists recursively
        return [convert_to_python(item) for item in obj]
    else:  # Keep numbers as they are
        return obj

def convert_lisp_file(input_file: str, output_file: str, module_name: str) -> None:
    """Convert a LISP unit definition file to Python."""
    # Read input file
    with open(input_file) as f:
        text = f.read()
    
    # Split into unit definitions
    units = split_unit_definitions(text)
    
    # Generate Python code
    lines = [
        '"""Generated unit initializations from LISP definitions."""',
        '',
        'from typing import Dict, Any',
        'from ..units import Unit, UnitRegistry',
        '',
        f'def initialize_{module_name}_units(registry: UnitRegistry) -> None:',
        f'    """Initialize {module_name} units."""',
        ''
    ]
    
    # Add unit initializations
    for unit in units:
        unit_code = convert_unit_to_python(unit)
        lines.extend('    ' + line if line else '' for line in unit_code.split('\n'))
    
    # Write output file
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: convert_units.py input.lisp output.py module_name")
        sys.exit(1)
        
    convert_lisp_file(sys.argv[1], sys.argv[2], sys.argv[3])
