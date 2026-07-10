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
