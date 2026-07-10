import os


class LanguageDetector:
    EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".cs": "c-sharp",
        ".cpp": "cpp",
        ".c": "c",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php"
    }

    FILENAMES = {
        "Dockerfile": "dockerfile",
        "Makefile": "makefile",
        "Jenkinsfile": "groovy",
        "pom.xml": "xml",
        "package.json": "json"
    }

    SHEBANGS = {
        "python": "python",
        "node": "javascript",
        "bash": "bash",
        "sh": "bash",
        "ruby": "ruby"
    }

    @classmethod
    def detect(cls, filepath: str) -> str:
        filename = os.path.basename(filepath)
        
        # 1. Filename match
        if filename in cls.FILENAMES:
            return cls.FILENAMES[filename]
        
        # 2. Extension match
        _, ext = os.path.splitext(filename)
        if ext.lower() in cls.EXTENSIONS:
            return cls.EXTENSIONS[ext.lower()]
        
        # 3. Shebang match
        try:
            with open(filepath, encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("#!"):
                    for key, lang in cls.SHEBANGS.items():
                        if key in first_line:
                            return lang
        except Exception:
            pass

        return "unsupported"
