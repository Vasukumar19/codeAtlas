(variable_declarator
  name: (identifier) @import.name
  value: (call_expression
    function: (identifier) @import.require
    (#eq? @import.require "require")
    arguments: (arguments (string (string_fragment) @import.source))
  )
) @import
