import os
from pathlib import Path
from app.parser.plugins.python_plugin import PythonPlugin

def test_fastapi_demo_parser():
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "python" / "fastapi_demo"
    filepaths = [
        str(fixtures_dir / "app.py"),
        str(fixtures_dir / "auth.py"),
        str(fixtures_dir / "users.py")
    ]
    
    result = PythonPlugin.parse_files(filepaths)
    
    assert len(result.files) == 3
    
    # 1. Validate Symbols
    # We expect AuthService class, login method, health_check function, login_route function, list_users function
    function_names = [s["name"] for s in result.symbols if s["type"] == "symbol.function.name"]
    class_names = [s["name"] for s in result.symbols if s["type"] == "symbol.class.name"]
    
    assert "AuthService" in class_names
    assert "login" in function_names
    assert "login_route" in function_names
    assert "health_check" in function_names
    assert "list_users" in function_names

    # 2. Validate Routes
    assert len(result.routes) > 0
    
    # Find /login route
    login_route = next((r for r in result.routes if r.get("path") == "/login"), None)
    assert login_route is not None
    assert login_route["method"] == "POST"
    assert login_route["handler"] == "login_route"
    
    # Find /health route
    health_route = next((r for r in result.routes if r.get("path") == "/health"), None)
    assert health_route is not None
    assert health_route["method"] == "GET"
    assert health_route["handler"] == "health_check"
    
    # Find / users route
    users_route = next((r for r in result.routes if r.get("path") == "/"), None)
    assert users_route is not None
    assert users_route["method"] == "GET"
    assert users_route["handler"] == "list_users"
    
    # 3. Validate Metadata
    assert result.metadata["total_todos"] == 1
