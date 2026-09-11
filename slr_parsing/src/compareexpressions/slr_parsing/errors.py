"""Error-recovery handlers for the parser."""


def new_root_on_error(parser, stack, a, input_tokens, tokens, output):
    # Finish the current root as if the input ended here, then parse the rest
    # (starting with the offending token) as a new root.
    tokens = [a]+tokens
    a = parser.end_token
    return stack, a, input_tokens, tokens, output
