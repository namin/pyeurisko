"""Convert Eurisko LISP unit definitions to Python format."""

import re
from typing import Dict, List, Any, Tuple, Optional

def parse_lisp_expression(s: str) -> Any:
    """Parse a LISP expression, handling nested lists and atoms."""
    s = s.strip()
    if not s:
        return None

    if s[0] == '(':
        # Parse a list
        stack = []
        current = []
        i = 1  # Skip first paren
        token = []
        
        while i < len(s):
            c = s[i]
            
            if c == '(':
                stack.append(current)
                current = []
            elif c == ')':
                if token:
                    current.append(''.join(token))
                    token = []
                if stack:
                    prev = stack.pop()
                    prev.append(current)
                    current = prev
                i += 1
                break
            elif c.isspace():
                if token:
                    current.append(''.join(token))
                    token = []
            else:
                token.append(c)
            i += 1

        return current
    else:
        # Parse an atom
        if s.isdigit():
            return int(s)
        elif s == 'nil':
            return None
        elif s == 't':
            return True
        else:
            return s

def parse_unit_def(text: str) -> Dict[str, Any]:
    """Parse a unit definition into a dictionary of properties."""
    # Extract unit name
    name_match = re.search(r'defunit\s+(\S+)', text)
    if not name_match:
        raise ValueError("Could not find unit name")
    name = name_match.group(1)
    
    # Split into properties
    lines = text.split('\n')
    props = {}
    current_prop = None
    current_value = []
    
    for line in lines[1:]:  # Skip defunit line
        line = line.strip()
        if not line or line.startswith(';'):
            continue
            
        # Check if this is a new property
        if not line.startswith('(') and not line.startswith(')'):
            # Save previous property if exists
            if current_prop and current_value:
                value = ' '.join(current_value)
                try:
                    props[current_prop] = parse_lisp_expression(value)
                except Exception as e:
                    print(f"Warning: Could not parse value for {current_prop}: {e}")
            
            current_prop = line
            current_value = []
        else:
            current_value.append(line)
    
    # Handle final property
    if current_prop and current_value:
        value = ' '.join(current_value)
        try:
            props[current_prop] = parse_lisp_expression(value)
        except Exception as e:
            print(f"Warning: Could not parse value for {current_prop}: {e}")
    
    return {
        'name': name,
        'properties': props
    }

def split_unit_definitions(text: str) -> List[str]:
    """Split a LISP file into individual unit definitions."""
    # Remove comments
    lines = []
    for line in text.split('\n'):
        comment_idx = line.find(';')
        if comment_idx >= 0:
            line = line[:comment_idx]
        if line.strip():
            lines.append(line)
    
    text = '\n'.join(lines)
    
    # Split on defunit
    units = []
    current = []
    paren_count = 0
    
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('(defunit') and paren_count == 0:
            if current:
                units.append('\n'.join(current))
            current = [line]
            paren_count = line.count('(') - line.count(')')
        else:
            current.append(line)
            paren_count += line.count('(') - line.count(')')
            
    if current:
        units.append('\n'.join(current))
        
    return units

def format_python_value(value: Any) -> str:
    """Format a parsed LISP value as Python code."""
    if isinstance(value, list):
        items = [format_python_value(x) for x in value]
        return f"[{', '.join(items)}]"
    elif value is None:
        return 'None'
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return f"'{value}'"

def convert_unit_to_python(unit_data: Dict[str, Any]) -> str:
    """Convert a parsed unit into Python initialization code."""
    name = unit_data['name']
    props = unit_data['properties']
    
    lines = []
    lines.append(f"# {name}")
    lines.append(f"unit = registry.create_unit('{name}')")
    
    # Set worth first if present
    if 'worth' in props:
        lines.append(f"unit.set_prop('worth', {props['worth']})")
    
    # Then other properties
    for prop, value in sorted(props.items()):
        if prop != 'worth':
            formatted_value = format_python_value(value)
            lines.append(f"unit.set_prop('{prop}', {formatted_value})")
    
    lines.append("")  # Add blank line
    return '\n'.join(lines)

def convert_lisp_file(input_file: str, output_file: str, module_name: str) -> None:
    """Convert a LISP unit definition file to Python."""
    # Read input file
    with open(input_file) as f:
        text = f.read()
    
    # Split into unit definitions
    unit_texts = split_unit_definitions(text)
    
    # Parse each unit
    units = []
    for unit_text in unit_texts:
        try:
            unit = parse_unit_def(unit_text)
            units.append(unit)
        except Exception as e:
            print(f"Warning: Could not parse unit: {e}")
            continue
    
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