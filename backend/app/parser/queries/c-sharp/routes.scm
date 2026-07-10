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
