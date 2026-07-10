from app.parser.registry import ParserRegistry
from app.parser.capabilities import CapabilityRegistry
from app.parser import initialize_registry

def test_registry_initialization():
    initialize_registry()
    assert "python" in ParserRegistry.list_supported_languages()
    
    python_plugin = ParserRegistry.get_plugin("python")
    assert python_plugin is not None
    
    caps = CapabilityRegistry.get("python")
    assert caps.get("ast") is True
