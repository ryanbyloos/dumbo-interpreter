from lark import Lark
from lark import Transformer
import sys

dumbo_grammar = Lark(
    r"""
    programme: txt | txt programme | dumbo_bloc | dumbo_bloc programme
    txt: /[a-zA-Z0-9;&<>"_\=\-\.\/\n\s:,]+/
    dumbo_bloc: "{{" expression_list "}}" | "{{" "}}"
    expression_list: expression ";" expression_list | expression ";"
    expression: "print" string_expression
               |for_loop
               |if_exp
               |variable ":=" string_expression
               |variable ":=" string_list
    string_expression: string | variable | string_expression "." string_expression
    string_list: "(" string_list_interior ")"
    string_list_interior: string | string "," string_list_interior
    variable: /[a-zA-Z0-9_]+/
    string: "'" txt "'"

    for_loop: "for" variable "in" string_list "do" expression_list "endfor"
             |"for" variable "in" variable "do" expression_list "endfor"
    if_exp: "if" bool "do" expression_list "endif"

    add: "+"
    dif: "-"
    mul: "*"
    div: "/"

    gt: ">"
    lt: "<"
    eq: "="
    neq:"!="
    
    int: /[0-9]+/ | "-" int
    var: int | variable
    cmp: gt | lt | eq | neq
    bool_exp: or | and

    bool: "true" | "false" | bool_exp | var cmp var

    or: "(" bool "or" bool ")"
    and: "(" bool "and" bool ")"

    %import common.WS
    %ignore WS
    """, start="programme")

if __name__ == "__main__":
    with open("exemples/data_t2.dumbo") as file:
        if (file != None):
            tree = dumbo_grammar.parse(file.read())
        else:
            print("SHEH")
    print(tree)