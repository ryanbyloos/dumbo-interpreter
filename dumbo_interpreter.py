from lark import Lark
from lark import Transformer
import sys
mapping = {}
dumbo_grammar = Lark(
    r"""
    programme: txt | txt programme | dumbo_bloc | dumbo_bloc programme
    txt: /[a-zA-Z0-9;&<>"_\=\-\.\/\n\s:,]+/
    dumbo_bloc: "{{" expression_list "}}" | "{{" "}}"
    expression_list: expression ";" expression_list | expression ";"
    expression: "print" string_expression
               |for_loop
               |if_exp
               |variable ":=" integer
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

    op: add|dif|mul|div

    integer:  integer op integer 
    | variable op integer
    | integer op variable
    | int

    var: int | variable
    cmp: gt | lt | eq | neq
    bool_exp: or | and
    true : "true"
    false: "false"
    bool: true | false | bool_exp | var cmp var

    or: "(" bool "or" bool ")"
    and: "(" bool "and" bool ")"

    %import common.WS
    %ignore WS
    """, start="programme")


def interprete(root, output_file):
    if(root.data == "programme"):
        for element in root.children:
            interprete(element, output_file)
    elif(root.data == "txt"):
        txt(root, output_file)
    elif(root.data == "dumbo_bloc"):
        for element in root.children:
            interprete(element, output_file)
    elif(root.data == "expression_list"):
        for element in root.children:
            interprete(element, output_file)
    elif(root.data == "expression"):
        if(root.children[0].data == "string_expression"):
            output_file.write(string_expression(root.children[0], output_file))
        elif(root.children[0].data == "variable"):
            variable_assignement(root, output_file)
        elif(root.children[0].data == "for_loop"):
            for_loop(root.children[0], output_file)
        elif(root.children[0].data == "if_exp"):
            if_exp(root.children[0], output_file)


def txt(tree, output_file):
    output_file.write(tree.children[0])


def string_expression(tree, output_file):
    if(tree.children[0].data == "string"):
        return str(tree.children[0].children[0].children[0])
    elif(tree.children[0].data == "variable"):
        return str(variable_value(tree.children[0]))
    else:
        return string_expression(tree.children[0], output_file)+string_expression(tree.children[1], output_file)


def variable(tree, output_file):
    output_file.write(mapping[tree.children[0]])


def variable_value(tree):
    return mapping[tree.children[0]]


def variable_assignement(tree, output_file):
    if(tree.children[1].data == "string_expression"):
        mapping[tree.children[0].children[0]] = string_expression(
            tree.children[1], output_file)
    elif(tree.children[1].data == "integer"):
        mapping[tree.children[0].children[0]] = integer(tree.children[1])
    elif(tree.children[1].data == "string_list"):
        res = []
        string_list_interior(tree.children[1].children[0], res)
        mapping[tree.children[0].children[0]] = tuple(res)


def integer(root):
    if(len(root.children) == 1):
        return int(root.children[0].children[0])
    else:
        if(root.children[0].data == "integer" and root.children[2].data == "integer"):
            return op(root.children[1], integer(root.children[0]),
                      integer(root.children[2]))
        elif(root.children[0].data == "variable" and root.children[2].data == "integer"):
            return op(root.children[1], variable_value(
                root.children[0]), integer(root.children[2]))
        elif(root.children[0].data == "integer" and root.children[2].data == "variable"):
            return op(root.children[1], integer(root.children[0]),
                      variable_value(root.children[2]))


def op(root, a, b):
    operation = str(root.children[0].data)
    if(operation == "add"):
        return a + b
    elif(operation == "dif"):
        return a - b
    elif(operation == "mul"):
        return a * b
    elif(operation == "div"):
        return a / b


def string_list_interior(root, res):
    if(len(root.children) > 1):
        res.append(str(root.children[0].children[0].children[0]))
        string_list_interior(root.children[1], res)
    else:
        res.append(str(root.children[0].children[0].children[0]))
        return res


def for_loop(root, output_file):
    Key = str(root.children[0].children[0])

    Temp = None

    if(mapping.__contains__(Key)):
        Temp = mapping.pop(Key)

    if(root.children[1].data == "string_list"):
        liste = string_list_interior(root.children[1], [])
    elif(root.children[1].data == "variable"):
        liste = mapping[root.children[1].children[0]]
    for element in liste:
        mapping[Key] = element
        interprete(root.children[2], output_file)
    if(Temp != None):
        mapping[Key] = Temp
    else:
        mapping.pop(Key)


def if_exp(root, output_file):
    if(boolean(root.children[0])):
        interprete(root.children[1], output_file)

def boolean(root):
    if(root.children[0].data == "bool_exp"):
        if(root.children[0].children[0].data == "or"):
            return or_execute(root.children[0].children[0])
        elif(root.children[0].children[0].data == "and"):
            return and_execute(root.children[0].children[0])
    elif(root.children[0].data == "var"):
        comp = root.children[1].data
        if(comp == "eq"):
            return var(root.children[0]) == var(root.children[2])
        elif(comp == "neq"):
            return var(root.children[0]) != var(root.children[2])
        elif(comp == "gt"):
            return var(root.children[0]) > var(root.children[2])
        elif(comp == "lt"):
            return var(root.children[0]) < var(root.children[2])
    elif(root.children[0].data == "true"):
        return True
    elif(root.childre[0].data == "false"):
        return False

def or_execute(root):
    return boolean(root.children[0]) or boolean(root.children[1])

def and_execute(root):
    return boolean(root.children[0]) and boolean(root.children[1])
    
def var(root):
    if(root.children[0] == "int"):
        return int(root.children[0].children[0])
    elif(root.children[0] == "variable"):
        return int(variable_value(root.children[0]))


if __name__ == "__main__":
    with open("exemples/data_t3.dumbo", "r") as variables:
        if (variables != None):
            tree_data = dumbo_grammar.parse(variables.read())
    with open("exemples/template3.dumbo", "r") as templates:
        if (templates != None):
            tree_template = dumbo_grammar.parse(templates.read())
    interprete(tree_data, None)
    with open("exemples/output.html", "w") as output:
        interprete(tree_template, output)
    

    
