(type_declaration
  (type_spec
    name: (type_identifier) @symbol.class.name)) @symbol.class

(function_declaration
  name: (identifier) @symbol.function.name) @symbol.function

(method_declaration
  name: (field_identifier) @symbol.method.name) @symbol.method
