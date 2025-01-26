import os
import importlib
import inspect

def list_heuristics(directory="eurisko/heuristics"):
    """List all heuristics with their names and docstrings."""
    heuristics = []
    
    # Get all Python files except __init__.py and base.py
    files = [f for f in os.listdir(directory) 
             if f.endswith('.py') 
             and f not in ['__init__.py', 'base.py', 'registry.py']]
    
    for file in sorted(files):
        module_name = file[:-3]  # Remove .py extension
        
        # Import the module
        module = importlib.import_module(f'eurisko.heuristics.{module_name}')
        
        # Look for setup function (they follow pattern setup_h*)
        setup_func = None
        for name, obj in inspect.getmembers(module):
            if name.startswith('setup_') and inspect.isfunction(obj):
                setup_func = obj
                break
        
        if setup_func:
            # Get the docstring
            docstring = inspect.getdoc(setup_func) or "No documentation available"
            
            # Add to list
            heuristics.append({
                'name': module_name,
                'docstring': docstring,
                'setup_function': setup_func.__name__
            })
    
    return heuristics

if __name__ == '__main__':
    heuristics = list_heuristics()
    print(f"Found {len(heuristics)} heuristics:\n")
    for h in heuristics:
        print(f"Name: {h['name']}")
        print(f"Setup: {h['setup_function']}")
        print(f"Description: {h['docstring']}\n")