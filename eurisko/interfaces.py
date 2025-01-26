"""Common interfaces and base classes for PyEurisko."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

@dataclass
class BaseEurisko:
    """Base data container for Eurisko objects."""
    name: str
    worth: int = 500
    properties: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    is_criterial: bool = False
    data_type: str = "any"
    dont_copy: bool = False
    double_check: bool = False
    super_slots: List[str] = field(default_factory=list)
    sub_slots: List[str] = field(default_factory=list)
    inverse: Optional[str] = None

class EuriskoObject(BaseEurisko):
    """Base class for all named objects in the system."""
    def __post_init__(self):
        """Initialize properties."""
        if not self.properties:
            self.properties = {}
            
        if 'worth' not in self.properties:
            self.properties['worth'] = self.worth
            
        # Store additional attributes as properties
        attrs = {
            'description': self.description,
            'is_criterial': self.is_criterial,
            'data_type': self.data_type,
            'dont_copy': self.dont_copy,
            'double_check': self.double_check,
            'super_slots': self.super_slots,
            'sub_slots': self.sub_slots,
            'inverse': self.inverse
        }
        
        for name, value in attrs.items():
            if value is not None:
                self.properties[name] = value
            elif name not in self.properties:
                # Set defaults for missing properties
                self.properties[name] = attrs[name]

    def worth_value(self) -> int:
        """Get the worth/importance value."""
        return self.get_prop('worth') or self.worth

    def get_prop(self, prop_name: str, default: Any = None) -> Any:
        """Get a property value."""
        return self.properties.get(prop_name, default)

    def set_prop(self, prop_name: str, value: Any) -> None:
        """Set a property value."""
        if self.validate_value(value):
            self.properties[prop_name] = value

    def has_prop(self, prop_name: str) -> bool:
        """Check if a property exists."""
        return prop_name in self.properties

    def add_prop(self, prop_name: str, value: Any, to_head: bool = False) -> None:
        """Add a value to a list property."""
        current = self.get_prop(prop_name)
        if current is None:
            current = []
            self.set_prop(prop_name, current)
        elif not isinstance(current, list):
            current = [current]
            self.set_prop(prop_name, current)
            
        if value not in current:
            if to_head:
                current.insert(0, value)
            else:
                current.append(value)

    def remove_prop(self, prop_name: str, value: Any = None) -> None:
        """Remove a property or value."""
        if value is None:
            self.properties.pop(prop_name, None)
        else:
            current = self.get_prop(prop_name)
            if isinstance(current, list) and value in current:
                current.remove(value)

    def validate_value(self, value: Any) -> bool:
        """Validate a value against the object's data type."""
        data_type = self.get_prop('data_type')
        if not data_type or data_type == 'any':
            return True
            
        if data_type == 'number':
            return isinstance(value, (int, float))
        elif data_type == 'text':
            return isinstance(value, str)
        elif data_type == 'bit':
            return value in (True, False, 0, 1)
        elif data_type == 'unit':
            # Import here to avoid circular imports
            from .units import Unit
            return isinstance(value, (str, Unit))
        elif data_type == 'lisp_fn':
            return callable(value)
            
        return True  # Unknown type defaults to accepting anything
