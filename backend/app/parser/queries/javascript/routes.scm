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
