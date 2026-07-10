from app.parser.detector import LanguageDetector

def test_language_detector_extension():
    assert LanguageDetector.detect("main.py") == "python"
    assert LanguageDetector.detect("app.js") == "javascript"
    assert LanguageDetector.detect("main.go") == "go"
    assert LanguageDetector.detect("Program.cs") == "c-sharp"
    assert LanguageDetector.detect("unknown.xyz") == "unsupported"

def test_language_detector_filename():
    assert LanguageDetector.detect("Dockerfile") == "dockerfile"
    assert LanguageDetector.detect("Makefile") == "makefile"
    assert LanguageDetector.detect("package.json") == "json"
