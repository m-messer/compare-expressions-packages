"""SLR(1) parser: table construction, scanning and parsing."""

import re

from .grammar import catch_undefined
from .tags import tag_transfer
from .tokens import ExprNode, Token


class SLR_Parser:

    def default_error_action(parser, stack, a, input_tokens, tokens, output):
        m = 70
        raise Exception(
            f"\n{'-'*m}\n" +
            f"ERROR:\n{'-'*m}\n" +
            f"accepted: {input_tokens[:-len(tokens)]}\n" +
            f"current: {a}, {parser._symbols_index[a]}\n" +
            f"remaining: {tokens}\n" +
            f"stack: {stack}\n" +
            f"output: {output}\n" +
            f"state: {parser.state_string(parser._states_index[stack[-1]])}\n" +
            f"{'-'*m}")

    def __init__(self, token_list, productions, start_symbol, end_symbol, null_symbol, error_handler=[], tag_handler=tag_transfer):
        self.token_list = sorted(token_list, key=lambda x: -len(x[0]))
        self.productions = productions
        self.start_symbol = start_symbol
        self.end_symbol = end_symbol
        self.null_symbol = null_symbol
        self.start_token = self.scan(start_symbol, mode="bnf")[0]
        self.end_token = self.scan(end_symbol, mode="bnf")[0]
        self.null_token = self.scan(null_symbol, mode="bnf")[0]
        start_token = self.start_token
        end_token = self.end_token
        null_token = self.null_token
        self.error_handler = error_handler
        self.tag_handler = tag_handler

        # Check if there are any duplicate productions
        checked_productions = []
        duplicate_error_string = []
        for prod in [(x[0], x[1]) for x in productions]:
            if prod in checked_productions:
                duplicate_error_string.append(f"duplicate: {prod}")
            checked_productions.append(prod)
        if len(duplicate_error_string) > 0:
            raise Exception("There are duplicate productions:\n" + "\n".join(duplicate_error_string))

        # Tokenize productions
        productions_token = [
            (self.scan(x[0], mode="bnf")[0], self.scan(x[1], mode="bnf")) for x in productions
        ]
        self.productions_token = productions_token

        # Analyse productions to find terminals and non-terminals
        non_terminals_token = []
        terminals_token = [self.end_token, self.null_token]
        for token in [prod[0] for prod in productions_token]:
            if token not in non_terminals_token:
                non_terminals_token.append(token)
        for production in productions_token:
            for token in production[1]:
                if token not in terminals_token and token not in non_terminals_token:
                    terminals_token.append(token)
        self.symbols = terminals_token+non_terminals_token
        self.terminals_token = terminals_token
        self.non_terminals_token = non_terminals_token

        # Reduction actions, indexed like the productions (not by body: productions
        # with equal bodies but different heads must keep their own actions)
        self.reductions = [production[2] for production in productions]

        # Compute dictionary with FIRST for all single tokens
        first_dict = {**{x: [x] for x in terminals_token}, **{x: [] for x in non_terminals_token}}
        lengths = [-1]*len(non_terminals_token)
        any_first_changed = True
        while any_first_changed:
            any_first_changed = False
            for k, x in enumerate(non_terminals_token):
                if lengths[k] != len(first_dict[x]):
                    lengths[k] = len(first_dict[x])
                    any_first_changed = True
            for nt in non_terminals_token:
                prods = [x[1] for x in productions_token if x[0] == nt]
                for prod in prods:
                    for token in prod:
                        for x in first_dict[token]:
                            if x not in first_dict[nt]:
                                first_dict[nt].append(x)
                        if null_token not in first_dict[token]:
                            break
        self._first_dict = first_dict

        # Compute dictionary with FOLLOW for all non_terminals
        first = self.first
        follow = {x: [] for x in non_terminals_token}
        follow[start_token].append(end_token)
        lengths = [-1]*len(non_terminals_token)
        while lengths != [len(follow[x]) for x in non_terminals_token]:
            lengths = [len(follow[x]) for x in non_terminals_token]
            for (head, body) in productions_token:
                for k, token in enumerate(body):
                    if token in non_terminals_token:
                        if null_token in self.first(body[k+1:]) or len(body[k+1:]) == 0:
                            for item in follow[head]:
                                if item not in follow[token]:
                                    follow[token].append(item)
                        for item in first(body[k+1:]):
                            if item != null_token and item not in follow[token]:
                                follow[token].append(item)
        self._follow = follow

        # Compute all states and the transitions between them
        closure = self.closure
        compute_transitions = self.compute_transitions
        start_productions = tuple([(k, 0) for k in range(0, len(productions_token)) if productions_token[k][0] == start_token])
        states = {start_productions: closure(start_productions)}
        transitions = {}
        new_states = [start_productions]
        while len(new_states) > 0:
            state = new_states.pop(0)
            trans = compute_transitions(closure(list(state)))
            transitions.update({state: trans})
            for t in trans:
                if tuple(t[1]) not in states.keys():
                    states.update({tuple(t[1]): closure(t[1])})
                    new_states.append(tuple(t[1]))
        self.states = states
        self.transitions = transitions

        # Create index dictionaries to simplify state table construction
        states_index = {}
        for i, s in enumerate(states):
            states_index.update({s: i, i: s})
        self._states_index = states_index

        symbols_index = {}
        symbols = terminals_token+non_terminals_token
        for j, h in enumerate(symbols):
            symbols_index.update({h: j, j: h})
        self._symbols_index = symbols_index

        # Compute parsing table
        parsing_table = []
        for i in range(0, len(states)):
            parsing_table.append([])
            for j in range(0, len(symbols)):
                parsing_table[i].append([])

        for state in states:
            for (production_index, dot_index) in closure(state):
                # Fill in shift actions and goto table
                (head, body) = productions_token[production_index]
                if dot_index < len(body):
                    a = body[dot_index]
                    table_entry = parsing_table[states_index[state]][symbols_index[a]]
                    for (symbol, next_state) in transitions[state]:
                        if symbol == a:
                            table_entry.append((production_index, states_index[tuple(next_state)]))
                            break
                elif head == self.start_token:
                    parsing_table[states_index[state]][symbols_index[self.end_token]].append((production_index, len(self.states)))
                else:
                    # Fill in reduce actions
                    for a in follow[head]:
                        table_entry = parsing_table[states_index[state]][symbols_index[a]]
                        table_entry.append((production_index, len(states)+production_index))

        # Choose correct table entry based on precedence,
        # precedence is determined by location in productions
        # array (higher index in array means higher precedence)
        for i in range(0, len(states)):
            for j in range(0, len(symbols)):
                table_entry = parsing_table[i][j]
                if len(table_entry) == 0:
                    # items_token gives a list of pairs that contain the parts of the production before and after the current point
                    items_token = [(productions_token[x[0]][1][0:x[1]], productions_token[x[0]][1][x[1]:]) for x in states_index[i]]
                    next_symbol = symbols_index[j]
                    parsing_table[i][j] = -1
                    for (index, condition) in enumerate([x[0] for x in self.error_handler], 2):
                        if condition(items_token, next_symbol):
                            parsing_table[i][j] = -index
                            break
                elif len(table_entry) == 1:
                    parsing_table[i][j] = table_entry[0][1]
                else:
                    precedence = table_entry[0][0]
                    index = 0
                    for k, action in enumerate(table_entry[1:], 1):
                        if precedence < action[0]:
                            precedence = action[0]
                            index = k
                    parsing_table[i][j] = table_entry[index][1]
        self.parsing_table = parsing_table

        # Check for unreachable states and reductions
        unreachable = list(range(0, len(states)+len(self.reductions)))
        for i in range(0, len(states)):
            for j in range(0, len(symbols)):
                if parsing_table[i][j] in unreachable:
                    unreachable.remove(parsing_table[i][j])
        self.parsing_table = parsing_table

        if len(unreachable) > 1:
            print("Unreachable states:")
            for x in [y for y in unreachable if y < len(states)]:
                print("\t"+self.state_string(self._states_index[x]))
            print("Unreachable reductions:")
            for x in [y for y in unreachable if y >= len(states) and y < len(states)+len(productions_token)]:
                print("\t"+self.productions[x-len(states)][0]+"-->"+str(self.productions[x-len(states)][1]))

        return

    def scan(self, expr, mode="expression"):
        token_list = self.token_list
        tokens = []

        def new_token(token_label, token_content, token_start, token_end):
            return Token(token_label, token_content, expr, token_start, token_end)

        token_catch_undefined = [x for x in token_list if len(x) > 2 and x[2] == catch_undefined]
        if len(token_catch_undefined) > 1:
            raise Exception("Only one token type can be used to catch undefined lexemes.")
        elif len(token_catch_undefined) < 1:
            token_catch_undefined = None
        else:
            token_catch_undefined = token_catch_undefined[0]

        if mode == "expression":
            token_rules = [x for x in token_list if len(x) > 2 and x[2] not in {None, catch_undefined}]
            token_symbols = [x for x in token_list if len(x) == 2]
        elif mode == "bnf":
            token_rules = []
            token_symbols = [(x[0], x[1]) for x in token_list]
        else:
            raise ValueError(f"Unknown scan mode {mode!r}, expected 'expression' or 'bnf'.")

        index = 0
        string = ""
        while index-len(string) < len(expr):
            end_token = None
            end_token_length = 0
            content = ""
            label = None
            for (re_content, current_label) in token_symbols:
                match_content = re.match(re_content, expr[index:])
                if match_content is not None:
                    current_content = match_content.group()
                    if len(current_content) > end_token_length:
                        content = current_content
                        end_token_length = len(content)
                        label = current_label
            for token in token_rules:
                current_label = token[1]
                match_rule, match_content = token[2](expr[index:])
                if match_rule is not None:
                    if len(match_rule) > end_token_length:
                        content = match_content
                        end_token_length = len(match_rule)
                        label = current_label
            if label is None:
                string = string+expr[index]
                index += 1
            else:
                end_token = new_token(label, content, index, index+end_token_length-1)
            if len(string) > 0 and (end_token is not None or index >= len(expr)):
                if token_catch_undefined is not None:
                    tokens.append(token_catch_undefined[2](token_catch_undefined[1], string, expr, index-len(string), index-1))
                else:
                    raise Exception(f"Undefined input: {string}")
                string = ""
            if end_token is not None:
                tokens.append(end_token)
                index += end_token_length
        return tokens

    def closure(self, item_set):
        non_terminals = self.non_terminals_token
        productions = self.productions_token
        # Items are represented as (i,j) where i indicates index
        # in production list and j position of inserted dot
        closure_set = []
        offset = -1
        new_items = item_set
        added_to_closure = [False]*len(non_terminals)
        while len(new_items) > 0:
            closure_set += new_items
            offset += len(new_items)
            new_items = []
            for item in closure_set:
                i = item[0]
                j = item[1]
                follow = None
                if j < len(productions[i][1]):
                    for k, nt in enumerate(non_terminals):
                        if productions[i][1][j] == nt:
                            follow = k
                            break
                    if follow is not None and not added_to_closure[follow]:
                        for k, production in enumerate(productions):
                            if production[0] == non_terminals[follow]:
                                new_items.append((k, 0))
                        added_to_closure[follow] = True
        return closure_set

    def compute_transitions(self, item_set):
        productions_token = self.productions_token
        transitions = []
        for item in item_set:
            i = item[0]
            j = item[1]
            if j < len(productions_token[i][1]):
                token = productions_token[i][1][j]
                if token not in [x[0] for x in transitions]:
                    transitions.append((token, [(i, j+1)]))
                else:
                    transitions[[x[0] for x in transitions].index(token)][1].append((i, j+1))
        return transitions

    def first(self, tokens):
        # Computes FIRST for strings of tokens
        null_token = self.null_token
        first_dict = self._first_dict
        if len(tokens) == 1:
            return first_dict[tokens[0]]
        fs = []
        for token in tokens:
            for item in first_dict[token]:
                if item not in fs and item != null_token:
                    fs.append(item)
            if token != null_token:
                break
        return fs

    def parsing_table_to_string(self):
        parsing_table = self.parsing_table
        symbols = [x.content for x in self.terminals_token+self.non_terminals_token]
        states = self.states
        parsing_table_string = ["\t"+"\t".join(symbols)+"\n"]

        for i in range(0, len(parsing_table)):
            parsing_table_string += [str(i)+"\t"]
            for j in range(0, len(parsing_table[i])):
                if parsing_table[i][j] < 0:
                    parsing_table_string += ['e'+str(-parsing_table[i][j])]
                elif parsing_table[i][j] < len(states):
                    parsing_table_string += ['s'+str(parsing_table[i][j])]
                else:
                    parsing_table_string += ['r'+str(parsing_table[i][j]-len(states))]
                parsing_table_string += ['\t']
            parsing_table_string += ['\n']

        return "".join(parsing_table_string)

    def state_string(self, state):
        items = self.closure(state)
        prod_strings = []
        for k in range(0, len(items)):
            production = self.productions_token[items[k][0]]
            dot_index = items[k][1]
            prod_string = "".join(x.content for x in production[1][0:dot_index])+"."+"".join(x.content for x in production[1][dot_index:])
            prod_strings.append(prod_string)
        return "I"+str(self._states_index[state])+": ("+", ".join(prod_strings)+")"

    def state_string_list(self, state):
        items = self.closure(state)
        prod_strings = []
        for k in range(0, len(items)):
            production = self.productions_token[items[k][0]]
            dot_index = items[k][1]
            prod_string = "".join(x.content for x in production[1][0:dot_index])+"."+"".join(x.content for x in production[1][dot_index:])
            prod_strings.append(prod_string)
        return ["I"+str(self._states_index[state])]+prod_strings

    def parsing_action(self, s, a):
        return self.parsing_table[s][self._symbols_index[a]]

    def parse(self, input_tokens, verbose=False):
        productions_token = self.productions_token
        tokens = list(input_tokens)
        if tokens[-1] != self.end_token:
            tokens += [self.end_token]
        a = tokens.pop(0)
        stack = [0]
        output = []
        while True:
            parse_action = self.parsing_action(stack[-1], a)
            while parse_action < 0:
                if parse_action == -1:
                    self.default_error_action(stack, a, input_tokens, tokens, output)
                else:
                    stack, a, input_tokens, tokens, output = self.error_handler[-2-parse_action][1](self, stack, a, input_tokens, tokens, output)
                parse_action = self.parsing_action(stack[-1], a)
            if parse_action < len(self.states):
                stack.append(parse_action)
                output.append(ExprNode(a, []))
                if verbose:
                    print("shift and transition to: "+self.state_string(self._states_index[parse_action])+"  \t"+str(output))
                a = tokens.pop(0)
            elif parse_action == len(self.states):
                if verbose:
                    print("ACCEPT")
                if len(tokens) > 0 and tokens != [self.end_token]:
                    output += self.parse(tokens)
                break
            elif parse_action <= len(self.states)+len(self.productions_token):
                production = productions_token[parse_action-len(self.states)]
                reduction = self.reductions[parse_action-len(self.states)]
                output = reduction(production, output, self.tag_handler)
                # print("-----------------------")
                # print(output[0].tree_string())
                # print("-----------------------")
                stack = stack[0:-len(production[1])]
                stack.append(self.parsing_action(stack[-1], production[0]))
                if verbose:
                    print("reduce by: "+str(production[0].content)+" --> "+"".join([x.content for x in production[1]])+"  \t"+str(output))
                    print("new state: "+self.state_string(self._states_index[stack[-1]]))
                    print("next input: "+str(a))
            else:
                m = 70
                raise Exception(f"{'-'*m}\nINVALID ENTRY:\n{'-'*m}\naccepted: {input_tokens[:-len(tokens)]}\ncurrent: {a}\nremaining: {tokens}\nstack: {stack}\noutput: {output}\n{'-'*m}")
                break
        return output
