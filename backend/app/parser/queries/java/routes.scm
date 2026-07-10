(method_declaration
  (modifiers
    (marker_annotation
      name: (identifier) @route.method
      (#match? @route.method ".*Mapping$")
    ) @route.annotation
  )
  name: (identifier) @route.handler
) @route
