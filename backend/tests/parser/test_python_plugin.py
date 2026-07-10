import tempfile
import os
from app.parser.plugins.python_plugin import PythonPlugin

def test_python_plugin_parse():
    content = """
def hello_world():
    # TODO: Implement this
    pass
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.py")
        with open(filepath, "w") as f:
            f.write(content)
            
        result = PythonPlugin.parse_files([filepath])
        
        assert len(result.files) == 1
        assert result.language == "python"
        assert result.metadata["total_loc"] == 4
        assert result.metadata["total_todos"] == 1
