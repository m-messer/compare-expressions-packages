"""Generic expression-parser builder on top of SLR_Parser."""

import re

from .actions import create_node, infix, relabel
from .grammar import catch_undefined
from .parser import SLR_Parser


def SLR_expression_parser(nodes=[], infix_operators=[], delimiters=[], undefined=None, costum_tokens=[], costum_productions=[], group_node=None, expression_node=None, start=None, null=None, end=None, error_handler=[]):
    infix_operators_dictionary = dict()
    unique_infix_operator_symbols = []
    for (symbol, label) in infix_operators:
        if label in infix_operators_dictionary.keys():
            infix_operators_dictionary[label] += [symbol]
        else:
            unique_infix_operator_symbols += [symbol]
            infix_operators_dictionary.update({label: [symbol]})
    infix_operators_token = []
    for (label, symbols) in infix_operators_dictionary.items():
        infix_operators_token.append(((" *("+"|".join([re.escape(s) for s in symbols])+") *"), label))

    if undefined is None:
        undefined_symbol = "UNDEFINED"
        undefined = (undefined_symbol, undefined_symbol, catch_undefined)
    else:
        undefined += (catch_undefined,)

    if expression_node is None:
        expression_node_symbol = "EXPRESSION_NODE"
        expression_node = (expression_node_symbol, expression_node_symbol, None)
    else:
        expression_node += (None,)

    if group_node is None:
        group_node_symbol = "GROUP_NODE"
        group_node = (group_node_symbol, group_node_symbol, None)

    if start is None:
        start_symbol = "START"
        start = (start_symbol, start_symbol)

    if end is None:
        end_symbol = "END"
        end = (end_symbol, end_symbol)

    if null is None:
        null_symbol = "NULL"
        null = (null_symbol, null_symbol)

    token_list = [undefined, null, expression_node, start, end]+nodes+infix_operators_token+costum_tokens

    productions = [(start[0], expression_node[0], relabel)]
    productions += [(expression_node[0], n[0], create_node) for n in nodes]
    productions += [(expression_node[0], undefined[0], create_node)]
    productions += [(expression_node[0], expression_node[0]+operator+expression_node[0], infix) for operator in unique_infix_operator_symbols]

    for (delims, action) in delimiters:
        token_list += [(re.escape(delims[0])+" *", "START_DELIMITER"), (" *"+re.escape(delims[1]), "END_DELIMITER")]
        productions += [(expression_node[0], delims[0]+expression_node[0]+delims[1], action)]

    productions += costum_productions

    return SLR_Parser(token_list, productions, start[1], end[1], null[1], error_handler=error_handler)
