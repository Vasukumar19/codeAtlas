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
