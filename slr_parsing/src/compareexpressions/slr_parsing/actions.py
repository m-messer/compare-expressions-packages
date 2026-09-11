"""Reduction actions: build the output tree when a production is reduced."""

from .tokens import ExprNode, Token, traverse_group, traverse_infix


def proceed(production, output, tag_handler):
    return output


def append(production, output, tag_handler):
    handle = production[1]
    children = output[1-len(handle):]
    output = output[0:(1-len(handle))]
    output[-1].children += children
    return output


def append_last(production, output, tag_handler):
    handle = production[1]
    last = output[-1]
    output = output[0:(1-len(handle))]
    output[-1].children.append(last)
    return output


def join(production, output, tag_handler):
    label = production[0].label
    handle = production[1]
    content = []
    for node in output[-len(handle):]:
        try:
            content.append(node.content_string())
        except Exception:
            content.append(node.content)
    joined_content = "".join(content)
    joined_end = output[-1].end
    output = output[0:(1-len(handle))]
    output[-1].label = label
    output[-1].content = joined_content
    output[-1].end = joined_end
    return output


def create_node(production, output, tag_handler):
    a = output.pop()
    node = ExprNode(a, [], tag_handler=tag_handler)
    output.append(node)
    return output


def relabel(production, output, tag_handler):
    a = output.pop()
    output.append(Token(production[0].label, a.content, a.original, a.start, a.end))
    return output


def group(number_of_elements, empty=False, delimiters=["", ""]):
    if number_of_elements < 1:
        raise ValueError("Groups must have at least one element.")

    def wrap(production, output, tag_handler):
        if empty:
            content = output[-number_of_elements:]
            output = output[0:-number_of_elements]
            end_delim = Token("START_DELIMITER", delimiters[1], content[0].original, content[0].start, content[0].end)
            start_delim = Token("END_DELIMITER", delimiters[0], content[0].original, content[0].start, content[0].end)
        else:
            end_delim = output.pop()
            content = output[-number_of_elements:]
            output = output[0:-number_of_elements]
            start_delim = output.pop()
        for k, elem in enumerate(content):
            if isinstance(elem, Token) and not isinstance(elem, ExprNode):
                content[k] = ExprNode(elem, [], tag_handler=tag_handler)
        output.append(
            ExprNode(
                Token(
                    "GROUP",
                    [start_delim.content, end_delim.content],
                    content[0].original,
                    start_delim.start, end_delim.end
                    ),
                content, traverse_step=traverse_group, tag_handler=tag_handler)
            )
        return output

    return wrap


def operate(number_of_elements, empty=False):
    # Zero is rejected too: output[-0:] would take the entire output stack.
    if number_of_elements < 1:
        raise ValueError("Operations must have at least one argument.")

    def wrap(production, output, tag_handler):
        if empty:
            end_index = output[-1].end
            content = output[-number_of_elements:]
            output = output[0:-number_of_elements]
        else:
            end_delim = output.pop()
            end_index = end_delim.end
            content = output[-number_of_elements:]
            output = output[0:-number_of_elements]
            _ = output.pop()
        for k, elem in enumerate(content):
            if isinstance(elem, Token) and not isinstance(elem, ExprNode):
                content[k] = ExprNode(elem, [], tag_handler=tag_handler)
        operation = output.pop()
        node = ExprNode(operation, content, tag_handler=tag_handler)
        node.end = end_index
        output.append(node)
        return output

    return wrap


def infix(production, output, tag_handler):
    right = output.pop()
    operator = output.pop()
    left = output.pop()
    output.append(ExprNode(operator, [left, right], traverse_step=traverse_infix, tag_handler=tag_handler))
    return output


def insert_infix(content, label):
    def apply(production, output, tag_handler):
        operator_token = Token(label, content, output[-1].original, len(output[-1].original), -1)
        return infix(production, output[0:-1]+[operator_token]+[output[-1]], tag_handler=tag_handler)
    return apply


def compose(*funcs):
    def composed_functions(production, output, tag_handler):
        for f in reversed(funcs):
            output = f(production, output, tag_handler)
        return output
    return composed_functions


def flatten(production, output, tag_handler):
    node = output[-1]
    flattened_children = []
    for child in node.children:
        if node.label == child.label and node.content == child.content:
            flattened_children += child.children
        else:
            flattened_children.append(child)
    node.children = flattened_children
    return output
