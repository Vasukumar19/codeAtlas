import os

files = {
    # PYTHON QUERIES
    "backend/app/parser/queries/python/symbols.scm": """
(function_definition
  name: (identifier) @symbol.function.name) @symbol.function

(class_definition
  name: (identifier) @symbol.class.name) @symbol.class
""",
    "backend/app/parser/queries/python/imports.scm": """
(import_statement) @import
(import_from_statement) @import
""",
    "backend/app/parser/queries/python/routes.scm": """
(decorated_definition
  (decorator
    (call
      function: (attribute
        attribute: (identifier) @route.method
      )
      arguments: (argument_list
        (string (string_content) @route.path)
      )
    )
  )
  definition: (function_definition
    name: (identifier) @route.handler
  )
) @route
""",

    # JAVASCRIPT QUERIES
    "backend/app/parser/queries/javascript/symbols.scm": """
(class_declaration
  name: (identifier) @symbol.class.name) @symbol.class

(function_declaration
  name: (identifier) @symbol.function.name) @symbol.function

(method_definition
  name: (property_identifier) @symbol.method.name) @symbol.method
""",
    "backend/app/parser/queries/javascript/imports.scm": """
(variable_declarator
  name: (identifier) @import.name
  value: (call_expression
    function: (identifier) @import.require
    (#eq? @import.require "require")
    arguments: (arguments (string (string_fragment) @import.source))
  )
) @import
""",
    "backend/app/parser/queries/javascript/routes.scm": """
(call_expression
  function: (member_expression
    object: (identifier)
    property: (property_identifier) @route.method
    (#match? @route.method "^(get|post|put|delete|patch)$")
  )
  arguments: (arguments
    (string (string_fragment) @route.path)
  )
) @route
""",

    # JAVA QUERIES
    "backend/app/parser/queries/java/symbols.scm": """
(class_declaration
  name: (identifier) @symbol.class.name) @symbol.class

(method_declaration
  name: (identifier) @symbol.method.name) @symbol.method
""",
    "backend/app/parser/queries/java/imports.scm": """
(import_declaration) @import
""",
    "backend/app/parser/queries/java/routes.scm": """
(method_declaration
  (modifiers
    (marker_annotation
      name: (identifier) @route.method
      (#match? @route.method ".*Mapping$")
    ) @route.annotation
  )
  name: (identifier) @route.handler
) @route
""",

    # GO QUERIES
    "backend/app/parser/queries/go/symbols.scm": """
(type_declaration
  (type_spec
    name: (type_identifier) @symbol.class.name)) @symbol.class

(function_declaration
  name: (identifier) @symbol.function.name) @symbol.function

(method_declaration
  name: (field_identifier) @symbol.method.name) @symbol.method
""",
    "backend/app/parser/queries/go/imports.scm": """
(import_spec) @import
""",
    "backend/app/parser/queries/go/routes.scm": """
(call_expression
  function: (selector_expression
    operand: (identifier)
    field: (field_identifier) @route.method
    (#match? @route.method "^(GET|POST|PUT|DELETE|PATCH)$")
  )
  arguments: (argument_list
    (interpreted_string_literal) @route.path
    (identifier) @route.handler
  )
) @route
""",

    # CSHARP QUERIES
    "backend/app/parser/queries/c-sharp/symbols.scm": """
(class_declaration
  name: (identifier) @symbol.class.name) @symbol.class

(method_declaration
  name: (identifier) @symbol.method.name) @symbol.method
""",
    "backend/app/parser/queries/c-sharp/imports.scm": """
(using_directive) @import
""",
    "backend/app/parser/queries/c-sharp/routes.scm": """
(method_declaration
  (attribute_list
    (attribute
      name: (identifier) @route.method
      (#match? @route.method "^Http(Get|Post|Put|Delete)$")
      (attribute_argument_list
        (attribute_argument
          (string_literal) @route.path
        )
      )
    )
  )
  name: (identifier) @route.handler
) @route
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
