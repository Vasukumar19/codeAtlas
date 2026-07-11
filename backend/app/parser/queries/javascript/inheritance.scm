(extends_clause
  [
    (identifier) @class.extends
    (member_expression property: (identifier) @class.extends)
  ]
)
(implements_clause
  [
    (identifier) @class.implements
    (member_expression property: (identifier) @class.implements)
  ]
)
