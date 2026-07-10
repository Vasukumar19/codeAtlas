(class_declaration
  name: (identifier) @symbol.class.name) @symbol.class

(function_declaration
  name: (identifier) @symbol.function.name) @symbol.function

(method_definition
  name: (property_identifier) @symbol.method.name) @symbol.method
