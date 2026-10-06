"""
phan_biet_code.py - Phân biệt loại code Rồng Thần (bản khổng lồ).

Nhiệm vụ:
    - phan_biet_code(code, goi_y): phân biệt loại code.
    - phan_biet_theo_noi_dung(code): đoán từ nội dung.
    - phan_biet_theo_task(task): đoán từ yêu cầu.
    - phat_hien_hon_hop(code): phát hiện code đa ngôn ngữ.
    - tach_code_hon_hop(code): tách code hỗn hợp.
    - nhan_dien_framework(code): nhận diện framework.
    - nhan_dien_phien_ban(code, ngon_ngu): nhận diện version.
    - de_xuat_ten_file(ngon_ngu, framework): đề xuất tên file.
    - trich_dependencies(code, ngon_ngu): trích thư viện cần cài.
    - phan_tich_chi_tiet(code): đếm dòng/hàm/class/comment.
    - phat_hien_style(code): phát hiện style code.

Hỗ trợ:
    - 60+ ngôn ngữ / định dạng.
    - 20+ framework / library.
    - 10 tính năng phân tích.

Tầng dữ liệu: Không.
"""

import re
import json


# ================================================================
# GHI LOG
# ================================================================
def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ================================================================
# BẢNG NHÃN NGÔN NGỮ
# ================================================================
NHAN_NGON_NGU = {
    # Web / Markup
    "html": "HTML", "htm": "HTML",
    "xml": "XML", "xhtml": "XHTML",
    "svg": "SVG", "mathml": "MathML",
    "markdown": "Markdown", "md": "Markdown",
    "latex": "LaTeX", "tex": "LaTeX",
    "rtf": "RTF",
    # Style
    "css": "CSS", "scss": "SCSS", "sass": "SASS", "less": "LESS",
    "stylus": "Stylus",
    # Script
    "python": "Python", "py": "Python", "py2": "Python 2", "py3": "Python 3",
    "javascript": "JavaScript", "js": "JavaScript",
    "typescript": "TypeScript", "ts": "TypeScript",
    "jsx": "JSX", "tsx": "TSX",
    "coffeescript": "CoffeeScript", "dart": "Dart",
    # Hệ thống / OOP
    "java": "Java", "kotlin": "Kotlin", "scala": "Scala", "groovy": "Groovy",
    "c": "C", "cpp": "C++", "csharp": "C#", "cs": "C#",
    "go": "Go", "golang": "Go",
    "rust": "Rust", "swift": "Swift",
    "objective-c": "Objective-C", "objc": "Objective-C",
    "d": "D", "nim": "Nim", "zig": "Zig",
    # Script khác
    "ruby": "Ruby", "rb": "Ruby",
    "php": "PHP", "perl": "Perl", "pl": "Perl",
    "lua": "Lua", "r": "R", "matlab": "MATLAB",
    "julia": "Julia",
    "elixir": "Elixir", "erlang": "Erlang",
    "haskell": "Haskell", "clojure": "Clojure",
    "scheme": "Scheme", "lisp": "Lisp",
    "fsharp": "F#", "ocaml": "OCaml",
    "prolog": "Prolog", "fortran": "Fortran",
    "cobol": "COBOL", "pascal": "Pascal",
    "ada": "Ada", "vhdl": "VHDL", "verilog": "Verilog",
    "assembly": "Assembly", "asm": "Assembly",
    # Query / Data
    "sql": "SQL", "mysql": "MySQL", "postgresql": "PostgreSQL",
    "plsql": "PL/SQL", "tsql": "T-SQL",
    "graphql": "GraphQL", "gql": "GraphQL",
    "json": "JSON", "json5": "JSON5", "jsonc": "JSONC",
    "yaml": "YAML", "yml": "YAML",
    "toml": "TOML", "ini": "INI", "cfg": "INI",
    "csv": "CSV", "tsv": "TSV",
    "protobuf": "Protocol Buffers", "proto": "Protocol Buffers",
    "avro": "Avro", "parquet": "Parquet",
    # Config / DevOps
    "dockerfile": "Dockerfile", "docker": "Dockerfile",
    "docker-compose": "Docker Compose",
    "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "nginx": "Nginx config", "apache": "Apache config",
    "procfile": "Procfile",
    "env": ".env", "dotenv": ".env",
    "makefile": "Makefile", "make": "Makefile",
    "terraform": "Terraform", "tf": "Terraform",
    "ansible": "Ansible", "jenkinsfile": "Jenkinsfile",
    "gitignore": ".gitignore", "editorconfig": ".editorconfig",
    # Shell
    "bash": "Bash", "sh": "Shell", "shell": "Shell",
    "zsh": "Zsh", "fish": "Fish",
    "powershell": "PowerShell", "ps1": "PowerShell",
    "cmd": "CMD", "bat": "Batch",
    # Khác
    "text": "Text", "txt": "Text",
    "hon_hop": "Hỗn hợp", "khong_ro": "Code",
}


def _lay_nhan(ngon_ngu):
    if not ngon_ngu:
        return "Code"
    return NHAN_NGON_NGU.get(ngon_ngu.lower(), ngon_ngu.upper())


# ================================================================
# BẢNG FRAMEWORK
# ================================================================
FRAMEWORK = {
    "react": {
        "ngon_ngu": "javascript",
        "dau_hieu": [
            r"import\s+React\b", r"from\s+['\"]react['\"]",
            r"useState\s*\(", r"useEffect\s*\(",
            r"<[A-Z]\w*\s*/?>", r"React\.createElement",
        ],
        "tai_lieu": "https://react.dev/",
        "ten_file": ["App.jsx", "App.js", "index.jsx"],
    },
    "vue": {
        "ngon_ngu": "javascript",
        "dau_hieu": [
            r"createApp\s*\(", r"defineComponent\s*\(",
            r"<template>", r"<script setup>",
            r"v-if=", r"v-for=", r"v-model=",
        ],
        "tai_lieu": "https://vuejs.org/",
        "ten_file": ["App.vue", "main.js"],
    },
    "svelte": {
        "ngon_ngu": "javascript",
        "dau_hieu": [r"\{#if\s", r"\{#each\s", r"\$:\s", r"export\s+let\s"],
        "tai_lieu": "https://svelte.dev/",
        "ten_file": ["App.svelte", "main.js"],
    },
    "angular": {
        "ngon_ngu": "typescript",
        "dau_hieu": [r"@Component\s*\(", r"@Injectable\s*\(", r"@NgModule\s*\("],
        "tai_lieu": "https://angular.io/",
        "ten_file": ["app.component.ts", "main.ts"],
    },
    "nextjs": {
        "ngon_ngu": "javascript",
        "dau_hieu": [
            r"from\s+['\"]next/", r"getServerSideProps", r"getStaticProps",
        ],
        "tai_lieu": "https://nextjs.org/",
        "ten_file": ["page.jsx", "layout.jsx"],
    },
    "express": {
        "ngon_ngu": "javascript",
        "dau_hieu": [
            r"require\(['\"]express['\"]\)",
            r"from\s+['\"]express['\"]",
            r"app\.(get|post|put|delete)\s*\(",
        ],
        "tai_lieu": "https://expressjs.com/",
        "ten_file": ["app.js", "server.js", "index.js"],
    },
    "django": {
        "ngon_ngu": "python",
        "dau_hieu": [
            r"from\s+django", r"import\s+django",
            r"models\.Model", r"\{\%.*\%\}",
        ],
        "tai_lieu": "https://www.djangoproject.com/",
        "ten_file": ["views.py", "models.py", "urls.py"],
    },
    "flask": {
        "ngon_ngu": "python",
        "dau_hieu": [
            r"from\s+flask\s+import", r"import\s+flask",
            r"Flask\s*\(__name__\)", r"@app\.route",
        ],
        "tai_lieu": "https://flask.palletsprojects.com/",
        "ten_file": ["app.py", "routes.py", "main.py"],
    },
    "fastapi": {
        "ngon_ngu": "python",
        "dau_hieu": [
            r"from\s+fastapi\s+import", r"FastAPI\s*\(",
            r"@app\.(get|post|put|delete)", r"BaseModel",
        ],
        "tai_lieu": "https://fastapi.tiangolo.com/",
        "ten_file": ["main.py", "app.py"],
    },
    "pytorch": {
        "ngon_ngu": "python",
        "dau_hieu": [r"import\s+torch", r"from\s+torch", r"nn\.Module", r"torch\.tensor"],
        "tai_lieu": "https://pytorch.org/",
        "ten_file": ["model.py", "train.py"],
    },
    "tensorflow": {
        "ngon_ngu": "python",
        "dau_hieu": [r"import\s+tensorflow", r"from\s+tensorflow", r"tf\.keras"],
        "tai_lieu": "https://www.tensorflow.org/",
        "ten_file": ["model.py", "train.py"],
    },
    "pandas": {
        "ngon_ngu": "python",
        "dau_hieu": [r"import\s+pandas", r"from\s+pandas", r"pd\.DataFrame"],
        "tai_lieu": "https://pandas.pydata.org/",
        "ten_file": ["analysis.py"],
    },
    "rails": {
        "ngon_ngu": "ruby",
        "dau_hieu": [r"Rails\.application", r"ActiveRecord::Base"],
        "tai_lieu": "https://rubyonrails.org/",
        "ten_file": ["app.rb", "config.ru"],
    },
    "laravel": {
        "ngon_ngu": "php",
        "dau_hieu": [r"Illuminate\\", r"use\s+Illuminate"],
        "tai_lieu": "https://laravel.com/",
        "ten_file": ["web.php", "Controller.php"],
    },
    "spring": {
        "ngon_ngu": "java",
        "dau_hieu": [r"@SpringBootApplication", r"@RestController", r"@Autowired"],
        "tai_lieu": "https://spring.io/",
        "ten_file": ["Application.java", "Controller.java"],
    },
    "dotnet": {
        "ngon_ngu": "csharp",
        "dau_hieu": [r"using\s+System", r"namespace\s+\w+", r"public\s+class"],
        "tai_lieu": "https://dotnet.microsoft.com/",
        "ten_file": ["Program.cs", "Startup.cs"],
    },
    "gin": {
        "ngon_ngu": "go",
        "dau_hieu": [r"github\.com/gin-gonic/gin", r"gin\.Default\(\)"],
        "tai_lieu": "https://gin-gonic.com/",
        "ten_file": ["main.go", "router.go"],
    },
    "actix": {
        "ngon_ngu": "rust",
        "dau_hieu": [r"use\s+actix_web", r"#\[actix_web::main\]"],
        "tai_lieu": "https://actix.rs/",
        "ten_file": ["main.rs"],
    },
    "tailwind": {
        "ngon_ngu": "html",
        "dau_hieu": [r"class=\"[^\"]*\b(flex|grid|p-\d|m-\d|text-\w+|bg-\w+)\b"],
        "tai_lieu": "https://tailwindcss.com/",
        "ten_file": ["index.html"],
    },
    "bootstrap": {
        "ngon_ngu": "html",
        "dau_hieu": [r"class=\"[^\"]*\b(container|row|col-|btn-|navbar)\b"],
        "tai_lieu": "https://getbootstrap.com/",
        "ten_file": ["index.html"],
    },
}


# ================================================================
# BẢNG DEPENDENCY (từ import → tên package pip/npm)
# ================================================================
DEPENDENCY_PIP = {
    "flask": "Flask", "django": "Django", "fastapi": "fastapi",
    "requests": "requests", "numpy": "numpy", "pandas": "pandas",
    "torch": "torch", "tensorflow": "tensorflow", "keras": "keras",
    "sklearn": "scikit-learn", "scipy": "scipy", "matplotlib": "matplotlib",
    "seaborn": "seaborn", "cv2": "opencv-python", "PIL": "Pillow",
    "bs4": "beautifulsoup4", "lxml": "lxml", "selenium": "selenium",
    "pymongo": "pymongo", "psycopg2": "psycopg2-binary",
    "mysql": "mysql-connector-python", "redis": "redis",
    "aiohttp": "aiohttp", "httpx": "httpx", "websockets": "websockets",
    "pydantic": "pydantic", "sqlalchemy": "SQLAlchemy",
    "jwt": "PyJWT", "bcrypt": "bcrypt", "dotenv": "python-dotenv",
    "yaml": "PyYAML", "toml": "toml", "jinja2": "Jinja2",
    "pytest": "pytest", "unittest": None,  # builtin
    "os": None, "sys": None, "re": None, "json": None, "time": None,
    "datetime": None, "random": None, "math": None, "collections": None,
    "itertools": None, "functools": None, "typing": None, "pathlib": None,
    "ast": None, "difflib": None, "hashlib": None, "secrets": None,
    "threading": None, "multiprocessing": None, "asyncio": None,
    "logging": None, "unittest": None, "csv": None, "io": None,
}


# ================================================================
# PHÂN BIỆT THEO NỘI DUNG
# ================================================================
def phan_biet_theo_noi_dung(code):
    """Đoán ngôn ngữ từ nội dung. Trả về (ngon_ngu, do_tin_cay)."""
    if not code or not isinstance(code, str):
        return "khong_ro", 0.0
    c = code.strip()
    if not c:
        return "khong_ro", 0.0

    # 1. HTML
    if re.search(r"<!DOCTYPE\s+html", c, re.I):
        return "html", 0.95
    if re.search(r"<html[\s>]", c, re.I):
        return "html", 0.9
    so_the = len(re.findall(r"<[a-zA-Z][^>]*>", c))
    if so_the >= 3 and re.search(r"</[a-zA-Z]+>", c):
        if re.search(r"<(div|span|p|a|ul|li|table|form|input|button|h[1-6])\b", c, re.I):
            return "html", 0.85

    # 2. SVG
    if re.search(r"<svg[\s>]", c, re.I):
        return "svg", 0.9

    # 3. XML
    if re.search(r"<\?xml\s", c, re.I):
        return "xml", 0.9

    # 4. JSON
    if (c.startswith("{") and c.endswith("}")) or (c.startswith("[") and c.endswith("]")):
        try:
            json.loads(c)
            return "json", 0.9
        except (json.JSONDecodeError, ValueError):
            pass

    # 5. YAML
    if re.search(r"^\s*\w+\s*:\s*.+$", c, re.M) and \
       not re.search(r"[{};]", c) and re.search(r"^\s*-\s+", c, re.M):
        return "yaml", 0.75
    if re.search(r"^---\s*$", c, re.M):
        return "yaml", 0.8

    # 6. TOML
    if re.search(r"^\[[\w.]+\]\s*$", c, re.M) and re.search(r"^\w+\s*=\s*.+$", c, re.M):
        return "toml", 0.75

    # 7. INI
    if re.search(r"^\[[\w.]+\]\s*$", c, re.M) and re.search(r"^\w+\s*=\s*.+$", c, re.M):
        return "ini", 0.7

    # 8. .env
    if re.search(r"^[A-Z_][A-Z0-9_]*\s*=\s*.+$", c, re.M) and \
       not re.search(r"[{};()]", c):
        return "env", 0.7

    # 9. Dockerfile
    if re.search(r"^\s*FROM\s+\S+", c, re.M) and \
       re.search(r"^\s*(RUN|COPY|CMD|ENTRYPOINT|WORKDIR|ENV)\b", c, re.M):
        return "dockerfile", 0.95

    # 10. Kubernetes
    if re.search(r"^apiVersion\s*:", c, re.M) and re.search(r"^kind\s*:", c, re.M):
        return "kubernetes", 0.9

    # 11. Docker Compose
    if re.search(r"^version\s*:\s*['\"]?\d", c, re.M) and \
       re.search(r"^services\s*:", c, re.M):
        return "docker-compose", 0.9

    # 12. Procfile
    if re.search(r"^(web|worker|release)\s*:\s*\S+", c, re.M) and len(c.split("\n")) <= 10:
        return "procfile", 0.8

    # 13. Makefile
    if re.search(r"^[\w.-]+\s*:\s*[\w\s.]*$", c, re.M) and "\t" in c:
        return "makefile", 0.8

    # 14. Nginx config
    if re.search(r"^\s*(server|http|events|location)\s*\{", c, re.M):
        return "nginx", 0.8

    # 15. Apache config
    if re.search(r"<VirtualHost\b", c, re.I):
        return "apache", 0.9

    # 16. Terraform
    if re.search(r"^\s*(resource|provider|variable|output)\s+[\"']", c, re.M):
        return "terraform", 0.85

    # 17. .gitignore
    if c.startswith("#") or re.match(r"^[\w.*/]+\s*$", c):
        if re.search(r"\b(node_modules|__pycache__|\.env|venv|dist|build)\b", c):
            return "gitignore", 0.7

    # 18. CSS
    if re.search(r"^[\s\S]*?[.#@a-zA-Z][\w-]*\s*\{[\s\S]*?:[\s\S]*?;[\s\S]*?\}", c):
        so_property = len(re.findall(r"[\w-]+\s*:\s*[^;]+;", c))
        if so_property >= 3 and not re.search(r"\bdef\s|\bclass\s+\w+\s*[:(]|\bimport\s+\w+", c):
            return "css", 0.8
    if re.search(r"^\s*@(media|import|mixin|include|keyframes)\b", c, re.M):
        if re.search(r"\$[\w-]+\s*:", c):
            return "scss", 0.85
        return "css", 0.75

    # 19. SQL
    if re.search(r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|WITH)\s", c, re.I):
        return "sql", 0.9

    # 20. GraphQL
    if re.search(r"^\s*(query|mutation|subscription|fragment|type|input)\s+\w+", c, re.M):
        return "graphql", 0.85

    # 21. Shell (Bash/Sh/Zsh)
    if re.search(r"^#!\s*/bin/(bash|sh|zsh|fish)", c):
        if "bash" in c[:50]:
            return "bash", 0.95
        if "zsh" in c[:50]:
            return "zsh", 0.95
        if "fish" in c[:50]:
            return "fish", 0.95
        return "sh", 0.95
    if re.search(r"^\s*(echo|cd|ls|mkdir|rm|cp|mv|grep|awk|sed|cat|chmod)\b", c, re.M) \
       and not re.search(r"\bdef\s|\bclass\s|\bimport\s+\w+", c):
        if re.search(r"\$\w+|\$\{", c) or c.startswith("#"):
            return "bash", 0.7

    # 22. PowerShell
    if re.search(r"\$(env|args|\?)", c) or re.search(r"^\s*(Get|Set|New|Remove)-\w+", c, re.M):
        return "powershell", 0.85

    # 23. Batch / CMD
    if re.search(r"^@?echo\s+off", c, re.I) or re.search(r"^\s*(if|for)\s+.*%\w+%", c, re.M):
        return "bat", 0.8

    # 24. Python 2 vs 3
    if re.search(r"^\s*print\s+['\"]", c, re.M) and \
       not re.search(r"print\s*\(", c):
        return "py2", 0.8
    if re.search(r"^\s*(def|class|import|from|if|for|while|try|with)\b", c, re.M):
        if re.search(r"print\s*\(", c) or "if __name__" in c:
            return "python", 0.9
        return "python", 0.8
    if re.search(r"^\s*@\w+", c, re.M):
        return "python", 0.8
    if re.search(r"^\s*print\s*\(", c, re.M):
        return "python", 0.75

    # 25. JavaScript / TypeScript
    if re.search(r"\b(function|const|let|var)\s+\w+", c) or \
       re.search(r"=>", c) or re.search(r"console\.log\s*\(", c):
        if re.search(r":\s*(string|number|boolean|any|void)\b", c) or \
           re.search(r"\b(interface|type|enum)\s+\w+", c):
            return "typescript", 0.85
        return "javascript", 0.85
    if re.search(r"^\s*(export|import)\s+.*\s+from\s+['\"]", c, re.M):
        return "javascript", 0.85

    # 26. Java
    if re.search(r"^\s*(public|private|protected)?\s*class\s+\w+", c, re.M) and \
       re.search(r"^\s*public\s+static\s+void\s+main", c, re.M):
        return "java", 0.9
    if re.search(r"^\s*(public|private|protected)\s+\w+", c, re.M) and \
       re.search(r"^\s*package\s+[\w.]+;", c, re.M):
        return "java", 0.85

    # 27. C++
    if re.search(r"#include\s*<\w+>", c) and \
       (re.search(r"std::\w+", c) or re.search(r"int\s+main\s*\(", c)):
        return "cpp", 0.9

    # 28. C
    if re.search(r"#include\s*<\w+\.h>", c) and re.search(r"int\s+main\s*\(", c):
        return "c", 0.85

    # 29. C#
    if re.search(r"using\s+System", c) and re.search(r"namespace\s+\w+", c):
        return "csharp", 0.9

    # 30. Go
    if re.search(r"^\s*package\s+\w+", c, re.M) and re.search(r"func\s+\w+\s*\(", c):
        return "go", 0.9

    # 31. Rust
    if re.search(r"\bfn\s+\w+\s*\(", c) and \
       (re.search(r"\blet\s+mut\b", c) or re.search(r"println!", c)):
        return "rust", 0.9

    # 32. Ruby
    if re.search(r"^\s*def\s+\w+", c, re.M) and \
       re.search(r"^\s*end\s*$", c, re.M) and \
       (re.search(r"puts\s", c) or re.search(r"require\s", c)):
        return "ruby", 0.85

    # 33. PHP
    if re.search(r"<\?php", c):
        return "php", 0.95

    # 34. Swift
    if re.search(r"^\s*import\s+(Foundation|UIKit|SwiftUI)", c, re.M) and \
       re.search(r"func\s+\w+\s*\(", c):
        return "swift", 0.85

    # 35. Kotlin
    if re.search(r"^\s*fun\s+\w+\s*\(", c, re.M) and \
       re.search(r"\b(val|var)\s+\w+", c):
        return "kotlin", 0.85

    # 36. R
    if re.search(r"<-", c) and re.search(r"\b(library|require)\s*\(", c):
        return "r", 0.8

    # 37. MATLAB
    if re.search(r"^\s*function\s+.*=.*\(", c, re.M) and \
       re.search(r"^\s*end\s*$", c, re.M) and re.search(r"%", c):
        return "matlab", 0.7

    # 38. Perl
    if re.search(r"^\s*use\s+strict", c, re.M) or re.search(r"my\s+\$\w+", c):
        return "perl", 0.85

    # 39. Lua
    if re.search(r"^\s*local\s+\w+", c, re.M) and \
       re.search(r"function\s+\w+.*end", c, re.S):
        return "lua", 0.8

    # 40. Elixir
    if re.search(r"defmodule\s+\w+", c) and re.search(r"IO\.puts", c):
        return "elixir", 0.85

    # 41. Haskell
    if re.search(r"^\s*main\s*::\s*IO", c, re.M) or re.search(r"^\s*where\b", c, re.M):
        return "haskell", 0.75

    # 42. Erlang
    if re.search(r"^-module\(", c, re.M) and re.search(r"^-export\(", c, re.M):
        return "erlang", 0.9

    # 43. Assembly
    if re.search(r"^\s*(section|global|mov|add|jmp|push|pop)\b", c, re.M):
        return "assembly", 0.75

    # 44. Markdown
    if re.search(r"^#{1,6}\s+.+$", c, re.M) or re.search(r"^\s*[-*]\s+.+$", c, re.M):
        if not re.search(r"[{};()]", c):
            return "markdown", 0.6

    # 45. LaTeX
    if re.search(r"\\documentclass|\\begin\{|\\end\{", c):
        return "latex", 0.9

    # 46. CSV
    cac_dong = [d for d in c.split("\n") if d.strip()]
    if len(cac_dong) >= 3 and all("," in d for d in cac_dong[:3]):
        # Kiểm tra số dấu phẩy giống nhau
        so_phay = [d.count(",") for d in cac_dong[:5]]
        if len(set(so_phay)) == 1 and so_phay[0] >= 1:
            return "csv", 0.75

    # 47. TSV
    if len(cac_dong) >= 3 and all("\t" in d for d in cac_dong[:3]):
        return "tsv", 0.75

    # 48. Text thuần
    if not re.search(r"[{}();=<>\[\]]", c):
        return "text", 0.5

    return "khong_ro", 0.3


# ================================================================
# PHÂN BIỆT THEO TASK
# ================================================================
def phan_biet_theo_task(noi_dung_task):
    """Đoán ngôn ngữ từ task. Trả về (ngon_ngu, do_tin_cay)."""
    if not noi_dung_task:
        return "khong_ro", 0.0
    t = noi_dung_task.lower()

    # HTML / Web
    if any(k in t for k in ("web", "trang web", "website", "giao diện",
                            "html", "css", "landing page", "form",
                            "giao diện", "responsive", "mobile-first")):
        return "html", 0.8

    # Python
    if any(k in t for k in ("python", "py", "hàm", "def", "class",
                            "script", "tool", "bot", "crawl",
                            "ai", "model", "machine learning",
                            "dự đoán", "phân tích dữ liệu", "pandas",
                            "numpy", "pytorch", "tensorflow")):
        return "python", 0.8

    # JavaScript
    if any(k in t for k in ("javascript", "js", "node", "react", "vue",
                            "frontend", "browser", "express", "nextjs")):
        return "javascript", 0.8

    # TypeScript
    if any(k in t for k in ("typescript", "ts", "angular", "typed")):
        return "typescript", 0.8

    # SQL
    if any(k in t for k in ("sql", "query", "select", "database",
                            "cơ sở dữ liệu", "truy vấn", "mysql",
                            "postgresql", "sqlite")):
        return "sql", 0.8

    # Bash / Shell
    if any(k in t for k in ("bash", "shell", "terminal", "command line",
                            "cmd", "script sh", "linux command")):
        return "bash", 0.8

    # Java
    if any(k in t for k in ("java", "spring", "spring boot")):
        return "java", 0.8

    # C++
    if any(k in t for k in ("c++", "cpp", "c plus plus")):
        return "cpp", 0.85

    # C#
    if any(k in t for k in ("c#", "csharp", ".net", "dotnet")):
        return "csharp", 0.85

    # Go
    if any(k in t for k in ("golang", "go lang", " gin ", "echo go")):
        return "go", 0.85

    # Rust
    if any(k in t for k in ("rust", "cargo", "actix")):
        return "rust", 0.85

    # PHP
    if any(k in t for k in ("php", "laravel")):
        return "php", 0.85

    # Ruby
    if any(k in t for k in ("ruby", "rails")):
        return "ruby", 0.85

    # Swift / Kotlin (Mobile)
    if any(k in t for k in ("swift", "ios", "iphone")):
        return "swift", 0.8
    if any(k in t for k in ("kotlin", "android")):
        return "kotlin", 0.8

    # Shell config
    if any(k in t for k in ("dockerfile", "docker file")):
        return "dockerfile", 0.85
    if any(k in t for k in ("docker-compose", "docker compose")):
        return "docker-compose", 0.85
    if any(k in t for k in ("kubernetes", "k8s", "kubectl")):
        return "kubernetes", 0.85

    # JSON / YAML / XML
    if any(k in t for k in ("json",)):
        return "json", 0.85
    if any(k in t for k in ("yaml", "yml")):
        return "yaml", 0.85
    if any(k in t for k in ("xml",)):
        return "xml", 0.85
    if any(k in t for k in ("toml",)):
        return "toml", 0.85
    if any(k in t for k in ("csv",)):
        return "csv", 0.85

    # Markdown
    if any(k in t for k in ("markdown", "readme")):
        return "markdown", 0.85

    # LaTeX
    if any(k in t for k in ("latex", "tex", "báo cáo khoa học")):
        return "latex", 0.85

    return "khong_ro", 0.3


# ================================================================
# NHẬN DIỆN FRAMEWORK
# ================================================================
def nhan_dien_framework(code):
    """
    Nhận diện framework trong code.
    Trả về list dict [{ ten, ngon_ngu, tai_lieu, ten_file }].
    """
    if not code:
        return []

    ket_qua = []
    for ten, thong_tin in FRAMEWORK.items():
        for dau_hieu in thong_tin["dau_hieu"]:
            try:
                if re.search(dau_hieu, code, re.I | re.M):
                    ket_qua.append({
                        "ten": ten,
                        "ngon_ngu": thong_tin["ngon_ngu"],
                        "tai_lieu": thong_tin["tai_lieu"],
                        "ten_file": thong_tin["ten_file"],
                    })
                    break
            except re.error:
                continue

    return ket_qua


# ================================================================
# NHẬN DIỆN PHIÊN BẢN
# ================================================================
def nhan_dien_phien_ban(code, ngon_ngu):
    """
    Nhận diện phiên bản ngôn ngữ.
    Trả về: str (version) hoặc "".
    """
    if not code or not ngon_ngu:
        return ""

    nn = ngon_ngu.lower()

    if nn in ("python", "py"):
        if re.search(r"^\s*print\s+['\"]", code, re.M) and not re.search(r"print\s*\(", code):
            return "Python 2"
        if "if __name__ == " in code or re.search(r"print\s*\(", code):
            return "Python 3"
        return "Python"

    if nn in ("javascript", "js"):
        if re.search(r"\bconst\b|\blet\b|=>|\basync\b|\bawait\b", code):
            return "ES6+"
        if re.search(r"\bvar\b", code):
            return "ES5"

    if nn in ("java",):
        if re.search(r"\brecord\s+\w+", code):
            return "Java 14+"
        if re.search(r"\bvar\s+\w+\s*=", code):
            return "Java 10+"
        return "Java 8+"

    return ""


# ================================================================
# ĐỀ XUẤT TÊN FILE
# ================================================================
def de_xuat_ten_file(ngon_ngu, framework=None, code=""):
    """
    Đề xuất tên file phù hợp cho ngôn ngữ / framework.
    Trả về list tên file gợi ý.
    """
    framework = framework or {}

    # Nếu framework có ten_file → ưu tiên
    if framework.get("ten_file"):
        return list(framework["ten_file"])

    if not ngon_ngu:
        return ["code.txt"]

    nn = ngon_ngu.lower()

    bang_ten = {
        "html": ["index.html", "main.html"],
        "css": ["style.css", "main.css"],
        "scss": ["style.scss", "_variables.scss"],
        "sass": ["style.sass"],
        "less": ["style.less"],
        "javascript": ["main.js", "app.js", "index.js"],
        "typescript": ["main.ts", "app.ts"],
        "jsx": ["App.jsx", "index.jsx"],
        "tsx": ["App.tsx"],
        "python": ["main.py", "app.py", "run.py"],
        "py2": ["main.py"],
        "py3": ["main.py"],
        "java": ["Main.java", "App.java"],
        "kotlin": ["Main.kt"],
        "scala": ["Main.scala"],
        "groovy": ["Main.groovy"],
        "c": ["main.c"],
        "cpp": ["main.cpp"],
        "csharp": ["Program.cs"],
        "cs": ["Program.cs"],
        "go": ["main.go"],
        "golang": ["main.go"],
        "rust": ["main.rs"],
        "swift": ["main.swift"],
        "ruby": ["main.rb", "app.rb"],
        "rb": ["main.rb"],
        "php": ["index.php"],
        "perl": ["main.pl"],
        "pl": ["main.pl"],
        "lua": ["main.lua"],
        "r": ["main.R", "analysis.R"],
        "matlab": ["main.m"],
        "julia": ["main.jl"],
        "elixir": ["main.ex", "app.ex"],
        "erlang": ["main.erl"],
        "haskell": ["Main.hs"],
        "sql": ["query.sql", "schema.sql"],
        "mysql": ["query.sql"],
        "postgresql": ["query.sql"],
        "json": ["data.json", "config.json"],
        "yaml": ["config.yaml", "data.yaml"],
        "yml": ["config.yml"],
        "toml": ["config.toml"],
        "ini": ["config.ini"],
        "cfg": ["config.cfg"],
        "csv": ["data.csv"],
        "tsv": ["data.tsv"],
        "markdown": ["README.md", "docs.md"],
        "md": ["README.md"],
        "latex": ["document.tex"],
        "tex": ["document.tex"],
        "dockerfile": ["Dockerfile"],
        "docker-compose": ["docker-compose.yml"],
        "kubernetes": ["deployment.yaml"],
        "nginx": ["nginx.conf"],
        "apache": ["apache.conf"],
        "makefile": ["Makefile"],
        "env": [".env", ".env.example"],
        "gitignore": [".gitignore"],
        "bash": ["script.sh", "run.sh"],
        "sh": ["script.sh"],
        "shell": ["script.sh"],
        "zsh": ["script.zsh"],
        "fish": ["script.fish"],
        "powershell": ["script.ps1"],
        "ps1": ["script.ps1"],
        "bat": ["script.bat"],
        "cmd": ["script.bat"],
        "svg": ["image.svg"],
        "xml": ["data.xml"],
        "graphql": ["schema.graphql"],
        "text": ["note.txt"],
        "txt": ["note.txt"],
    }

    return bang_ten.get(nn, ["code.txt"])


# ================================================================
# TRÍCH DEPENDENCIES
# ================================================================
def trich_dependencies(code, ngon_ngu):
    """
    Trích danh sách thư viện cần cài từ code.

    Trả về dict:
        {
            can_cai: list[str],       # package cần pip/npm install
            co_san: list[str],        # builtin (không cần cài)
            tat_ca: list[str],
        }
    """
    ket_qua = {"can_cai": [], "co_san": [], "tat_ca": []}

    if not code or not ngon_ngu:
        return ket_qua

    nn = ngon_ngu.lower()

    # Python
    if nn in ("python", "py", "py2", "py3"):
        # from X import Y
        imports1 = re.findall(r"^\s*from\s+(\w+)", code, re.M)
        # import X
        imports2 = re.findall(r"^\s*import\s+(\w+)", code, re.M)

        tat_ca = list(dict.fromkeys(imports1 + imports2))

        for mod in tat_ca:
            if mod in DEPENDENCY_PIP:
                package = DEPENDENCY_PIP[mod]
                if package is None:
                    ket_qua["co_san"].append(mod)
                else:
                    ket_qua["can_cai"].append(package)
            else:
                # Chưa biết → cho vào can_cai (người dùng tự kiểm)
                ket_qua["can_cai"].append(mod)

        ket_qua["tat_ca"] = tat_ca

    # JavaScript / TypeScript
    elif nn in ("javascript", "js", "typescript", "ts", "jsx", "tsx"):
        # import X from 'Y'
        imports1 = re.findall(r"from\s+['\"]([^'\"]+)['\"]", code)
        # require('X')
        imports2 = re.findall(r"require\s*\(\s*['\"]([^'\"]+)['\"]", code)

        tat_ca = list(dict.fromkeys(imports1 + imports2))

        for mod in tat_ca:
            # Bỏ đường dẫn tương đối
            if mod.startswith(".") or mod.startswith("/"):
                continue
            # Bỏ module con (abc/xyz → abc)
            if "/" in mod:
                mod = mod.split("/")[0]
            ket_qua["can_cai"].append(mod)

        ket_qua["tat_ca"] = tat_ca

    # Java
    elif nn == "java":
        imports = re.findall(r"^\s*import\s+([\w.]+);", code, re.M)
        ket_qua["tat_ca"] = imports
        ket_qua["can_cai"] = list(set(i.rsplit(".", 1)[0] for i in imports))

    return ket_qua


# ================================================================
# PHÂN TÍCH CHI TIẾT
# ================================================================
def phan_tich_chi_tiet(code):
    """
    Đếm dòng, hàm, class, comment, và các chỉ số khác.
    """
    ket_qua = {
        "tong_dong": 0,
        "dong_trong": 0,
        "dong_code": 0,
        "dong_comment": 0,
        "so_ham": 0,
        "so_class": 0,
        "so_bien": 0,
        "do_dai_max": 0,
        "ky_tu": 0,
    }

    if not code:
        return ket_qua

    cac_dong = code.split("\n")
    ket_qua["tong_dong"] = len(cac_dong)
    ket_qua["ky_tu"] = len(code)

    for dong in cac_dong:
        dong_strip = dong.strip()
        if not dong_strip:
            ket_qua["dong_trong"] += 1
        elif dong_strip.startswith("#") or dong_strip.startswith("//") or \
             dong_strip.startswith("/*") or dong_strip.startswith("*") or \
             dong_strip.startswith("--"):
            ket_qua["dong_comment"] += 1
        else:
            ket_qua["dong_code"] += 1

        if len(dong) > ket_qua["do_dai_max"]:
            ket_qua["do_dai_max"] = len(dong)

    # Đếm hàm / class (Python + JS + Java)
    ket_qua["so_ham"] = len(re.findall(
        r"^\s*(def|function|func|fn|fun)\s+\w+", code, re.M
    ))
    ket_qua["so_class"] = len(re.findall(
        r"^\s*class\s+\w+", code, re.M
    ))
    ket_qua["so_bien"] = len(re.findall(
        r"^\s*\w+\s*=\s*[^=]", code, re.M
    ))

    return ket_qua


# ================================================================
# PHÁT HIỆN STYLE
# ================================================================
def phat_hien_style(code):
    """
    Phát hiện style code.
    Trả về dict { ten_style: True/False }.
    """
    ket_qua = {
        "snake_case": False,
        "camelCase": False,
        "PascalCase": False,
        "kebab-case": False,
        "UPPER_CASE": False,
        "co_unicode": False,
        "co_tab": False,
        "co_trailing_space": False,
    }

    if not code:
        return ket_qua

    # snake_case: abc_xyz
    if re.search(r"\b[a-z]+_[a-z]+\b", code):
        ket_qua["snake_case"] = True

    # camelCase: abcXyz (viết hoa giữa)
    if re.search(r"\b[a-z]+[A-Z][a-z]+\b", code):
        ket_qua["camelCase"] = True

    # PascalCase: AbcXyz
    if re.search(r"\b[A-Z][a-z]+[A-Z][a-z]+\b", code):
        ket_qua["PascalCase"] = True

    # kebab-case: abc-xyz
    if re.search(r"\b[a-z]+-[a-z]+\b", code):
        ket_qua["kebab-case"] = True

    # UPPER_CASE
    if re.search(r"\b[A-Z]{2,}(_[A-Z]+)*\b", code):
        ket_qua["UPPER_CASE"] = True

    # Unicode (tiếng Việt, emoji)
    if any(ord(c) > 127 for c in code):
        ket_qua["co_unicode"] = True

    # Tab
    if "\t" in code:
        ket_qua["co_tab"] = True

    # Trailing space
    for dong in code.split("\n"):
        if dong != dong.rstrip():
            ket_qua["co_trailing_space"] = True
            break

    return ket_qua


# ================================================================
# PHÁT HIỆN CODE HỖN HỢP
# ================================================================
def phat_hien_hon_hop(code):
    """Kiểm tra code có nhiều ngôn ngữ. Trả về (hon_hop, danh_sach)."""
    if not code:
        return False, []

    danh_sach = []

    if re.search(r"<(html|body|div|script|style)\b", code, re.I):
        danh_sach.append("html")

    if re.search(r"^\s*def\s+\w+\s*\(", code, re.M):
        if "html" not in danh_sach:
            danh_sach.append("python")

    if re.search(r"<script\b", code, re.I) or \
       re.search(r"\b(function|const|let)\s+\w+\s*[=(]", code):
        if "javascript" not in danh_sach:
            danh_sach.append("javascript")

    if re.search(r"<style\b", code, re.I) or \
       re.search(r"[\w-]+\s*:\s*[^;]+;\s*[\w-]+\s*:", code):
        if "css" not in danh_sach:
            danh_sach.append("css")

    if len(danh_sach) >= 2:
        return True, danh_sach
    return False, danh_sach


# ================================================================
# TÁCH CODE HỖN HỢP
# ================================================================
def tach_code_hon_hop(code):
    """Tách code hỗn hợp thành từng phần."""
    if not code:
        return []

    ket_qua = []

    for match in re.finditer(r"<style[^>]*>([\s\S]*?)</style>", code, re.I):
        ket_qua.append({"ngon_ngu": "css", "nhan": "CSS", "code": match.group(1).strip()})

    for match in re.finditer(r"<script[^>]*>([\s\S]*?)</script>", code, re.I):
        ket_qua.append({"ngon_ngu": "javascript", "nhan": "JavaScript", "code": match.group(1).strip()})

    html_con_lai = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", code, flags=re.I)
    html_con_lai = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", html_con_lai, flags=re.I)
    html_con_lai = html_con_lai.strip()

    if html_con_lai and re.search(r"<[a-zA-Z]", html_con_lai):
        ket_qua.insert(0, {"ngon_ngu": "html", "nhan": "HTML", "code": html_con_lai})

    if not ket_qua and re.search(r"^\s*def\s+\w+", code, re.M):
        ket_qua.append({"ngon_ngu": "python", "nhan": "Python", "code": code.strip()})

    if not ket_qua:
        nn, _ = phan_biet_theo_noi_dung(code)
        ket_qua.append({"ngon_ngu": nn, "nhan": _lay_nhan(nn), "code": code.strip()})

    return ket_qua


# ================================================================
# NHẬN DIỆN KHUNG PHÙ HỢP
# ================================================================
def nhan_dien_khung_phu_hop(code):
    """Trả về danh sách khung code cần hiển thị."""
    if not code:
        return []

    hon_hop, _ = phat_hien_hon_hop(code)
    if hon_hop:
        return tach_code_hon_hop(code)

    ket_qua = phan_biet_code(code)
    return [{
        "ngon_ngu": ket_qua["ngon_ngu"],
        "nhan": ket_qua["nhan"],
        "code": code,
    }]


# ================================================================
# PHÂN BIỆT CHÍNH
# ================================================================
def phan_biet_code(code, ngon_ngu_goi_y=""):
    """
    Phân biệt loại code — API chính.

    Trả về dict đầy đủ:
        ngon_ngu, nhan, do_tin_cay, hon_hop, danh_sach_ngon_ngu,
        framework, phien_ban, ten_file_goi_y, dependencies,
        chi_tiet, style.
    """
    ket_qua = {
        "ngon_ngu": "khong_ro",
        "nhan": "Code",
        "do_tin_cay": 0.0,
        "hon_hop": False,
        "danh_sach_ngon_ngu": [],
        "framework": [],
        "phien_ban": "",
        "ten_file_goi_y": [],
        "dependencies": {},
        "chi_tiet": {},
        "style": {},
    }

    if not code or not isinstance(code, str):
        return ket_qua

    # 1. Gợi ý
    if ngon_ngu_goi_y:
        nn = ngon_ngu_goi_y.lower()
        if nn in NHAN_NGON_NGU:
            ket_qua["ngon_ngu"] = nn
            ket_qua["nhan"] = _lay_nhan(nn)
            ket_qua["do_tin_cay"] = 0.9
            ket_qua["danh_sach_ngon_ngu"] = [nn]
            _bo_sung_thong_tin(ket_qua, code, nn)
            return ket_qua

    # 2. Đoán từ nội dung
    nn, dtc = phan_biet_theo_noi_dung(code)

    # 3. Kiểm tra hỗn hợp
    hon_hop, danh_sach = phat_hien_hon_hop(code)
    if hon_hop:
        ket_qua["ngon_ngu"] = "hon_hop"
        ket_qua["nhan"] = "Hỗn hợp"
        ket_qua["do_tin_cay"] = 0.7
        ket_qua["hon_hop"] = True
        ket_qua["danh_sach_ngon_ngu"] = danh_sach
        return ket_qua

    # 4. Kết quả
    if nn != "khong_ro":
        ket_qua["ngon_ngu"] = nn
        ket_qua["nhan"] = _lay_nhan(nn)
        ket_qua["do_tin_cay"] = dtc
        ket_qua["danh_sach_ngon_ngu"] = [nn]
        _bo_sung_thong_tin(ket_qua, code, nn)

    return ket_qua


def _bo_sung_thong_tin(ket_qua, code, ngon_ngu):
    """Bổ sung thông tin chi tiết cho kết quả."""
    # Framework
    ket_qua["framework"] = nhan_dien_framework(code)

    # Phiên bản
    ket_qua["phien_ban"] = nhan_dien_phien_ban(code, ngon_ngu)

    # Tên file gợi ý
    fw = ket_qua["framework"][0] if ket_qua["framework"] else None
    ket_qua["ten_file_goi_y"] = de_xuat_ten_file(ngon_ngu, fw, code)

    # Dependencies
    ket_qua["dependencies"] = trich_dependencies(code, ngon_ngu)

    # Chi tiết
    ket_qua["chi_tiet"] = phan_tich_chi_tiet(code)

    # Style
    ket_qua["style"] = phat_hien_style(code)


# ================================================================
# HÀM PHỤ
# ================================================================
def lay_nhan(ngon_ngu):
    return _lay_nhan(ngon_ngu)


def danh_sach_ngon_ngu_ho_tro():
    return sorted(set(NHAN_NGON_NGU.values()))


def danh_sach_framework_ho_tro():
    return sorted(FRAMEWORK.keys())


def la_html(code):
    nn, dtc = phan_biet_theo_noi_dung(code)
    return nn == "html" and dtc >= 0.6


def la_python(code):
    nn, dtc = phan_biet_theo_noi_dung(code)
    return nn == "python" and dtc >= 0.6


def la_javascript(code):
    nn, dtc = phan_biet_theo_noi_dung(code)
    return nn == "javascript" and dtc >= 0.6


def dem_dong_code(code):
    if not code:
        return 0
    return sum(1 for d in code.split("\n") if d.strip())


# ================================================================
# PHÂN TÍCH TỔNG HỢP (gộp tất cả)
# ================================================================
def phan_tich_tong_hop(code, ngon_ngu_goi_y=""):
    """
    API gộp: phân tích code toàn diện.

    Trả về dict đầy đủ gồm tất cả thông tin:
    ngôn ngữ, framework, dependencies, chi tiết, style, tên file, phiên bản.
    """
    ket_qua = phan_biet_code(code, ngon_ngu_goi_y)

    # Thêm tóm tắt
    tom_tat = []
    tom_tat.append(f"Ngôn ngữ: {ket_qua['nhan']} ({ket_qua['do_tin_cay']:.0%})")

    if ket_qua["phien_ban"]:
        tom_tat.append(f"Phiên bản: {ket_qua['phien_ban']}")

    if ket_qua["framework"]:
        ten_fw = [fw["ten"] for fw in ket_qua["framework"]]
        tom_tat.append(f"Framework: {', '.join(ten_fw)}")

    if ket_qua["ten_file_goi_y"]:
        tom_tat.append(f"Tên file: {ket_qua['ten_file_goi_y'][0]}")

    dep = ket_qua["dependencies"]
    if dep.get("can_cai"):
        tom_tat.append(f"Cần cài: {', '.join(dep['can_cai'][:5])}")

    ct = ket_qua["chi_tiet"]
    if ct:
        tom_tat.append(
            f"Code: {ct.get('dong_code', 0)} dòng, "
            f"{ct.get('so_ham', 0)} hàm, "
            f"{ct.get('so_class', 0)} class"
        )

    ket_qua["tom_tat"] = "\n".join(tom_tat)
    return ket_qua