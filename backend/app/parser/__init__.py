from app.parser.registry import ParserRegistry
from app.parser.plugins.python_plugin import PythonPlugin
from app.parser.plugins.javascript_plugin import JavaScriptPlugin
from app.parser.plugins.typescript_plugin import TypeScriptPlugin
from app.parser.plugins.java_plugin import JavaPlugin
from app.parser.plugins.go_plugin import GoPlugin
from app.parser.plugins.csharp_plugin import CSharpPlugin
from app.parser.plugins.cpp_plugin import CppPlugin

def initialize_registry():
    ParserRegistry.register("python", PythonPlugin, {"ast": True, "metadata": True})
    ParserRegistry.register("javascript", JavaScriptPlugin, {"ast": True, "metadata": True})
    ParserRegistry.register("typescript", TypeScriptPlugin, {"ast": True, "metadata": True})
    ParserRegistry.register("java", JavaPlugin, {"ast": True, "metadata": True})
    ParserRegistry.register("go", GoPlugin, {"ast": True, "metadata": True})
    ParserRegistry.register("c-sharp", CSharpPlugin, {"ast": True, "metadata": True})
    ParserRegistry.register("cpp", CppPlugin, {"ast": True, "metadata": True})

initialize_registry()
