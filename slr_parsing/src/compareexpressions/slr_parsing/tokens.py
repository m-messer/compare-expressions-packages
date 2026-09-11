"""Tokens, expression-tree nodes and tree traversal steps."""


def traverse_prefix(expr_node, action):
    out = [(True, action(expr_node))]
    for x in expr_node.children:
        out += [(False, x)]
    return out


def traverse_postfix(expr_node, action):
    out = []
    for x in expr_node.children:
        out += [(False, x)]
    return out+[(True, action(expr_node))]


def traverse_infix(expr_node, action):
    out = []
    for x in expr_node.children[0:-1]:
        out += [(False, x), (True, action(expr_node))]
    return out+[(False, expr_node.children[-1])]


def traverse_group(expr_node, action):
    out = [(True, action(expr_node)[0])]
    for x in expr_node.children:
        out += [(False, x)]
    return out+[(True, action(expr_node)[1])]


class Token:

    def __init__(self, label, content, original, start, end):
        self.label = label
        self.content = content
        self.original = original
        self.start = start
        self.end = end
        return

    def __eq__(self, other):
        return isinstance(other, Token) and self.label == other.label

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return str(self.label)+": "+str(self.content)

    def __repr__(self):
        # REMARK(KarlLundengaard): This is not a good repr function, but it means that the most
        # relevant info is printed in the watch window of my preferred debugger
        return str(self.label)+": "+str(self.content)


class ExprNode(Token):

    def __init__(self, token, children, tag_handler=None, tags=None, traverse_step=traverse_prefix):
        super().__init__(token.label, token.content, token.original, token.start, token.end)
        self.tags = set()
        self.children = []
        for child in children:
            if isinstance(child, ExprNode):
                self.children.append(child)
            elif isinstance(child, Token):
                self.children.append(ExprNode(child, []))
            else:
                raise Exception(f"Invalid child {str(child)}")
        self._traverse_step = traverse_step
        if tag_handler is not None:
            self.tags = tag_handler(self)
        else:
            self.tags = set(tags) if tags is not None else set()
        return

    def copy(self):
        token = Token(self.label, self.content, self.original, self.start, self.end)
        children = []
        for child in self.children:
            children.append(child.copy())
        return ExprNode(token, children, tags=self.tags, traverse_step=self._traverse_step)

    def tree_string(self):
        s = str(self)
        for k, child in enumerate(self.children):
            padding = "\n|   " if k < len(self.children)-1 else "\n    "
            s += "\n"+str(k)+": "+child.tree_string().replace("\n", padding)
        return s

    def content_string(self, max_depth=None):
        output = self.traverse(lambda x: x.content, max_depth)
        return "".join(output)

    def traverse(self, action, max_depth=None):
        stack = [x+(0,) for x in self._traverse_step(self, action)[::-1]]
        output = []
        while len(stack) > 0:
            (is_output, elem, depth) = stack.pop()
            if max_depth is None or depth <= max_depth:
                if is_output:
                    output.append(elem)
                else:
                    stack += [x+(depth+1,) for x in elem._traverse_step(elem, action)[::-1]]
        return output

    def original_string(self):
        left_children = self.children
        right_children = self.children
        start = self.start
        end = self.end
        while len(left_children) > 0:
            start = min(start, left_children[0].start)
            left_children = left_children[0].children
        while len(right_children) > 0:
            end = max(end, right_children[-1].end)
            right_children = right_children[-1].children
        return self.original[start:end+1]

    def __str__(self):
        tags = str(self.tags) if len(self.tags) > 0 else "{}"
        return str(self.label)+": "+str(self.content)+" tags: "+tags

    def __repr__(self):
        # REMARK(KarlLundengaard): This is not a good repr function, but it means that the most
        # relevant info is printed in the watch window of my preferred debugger
        return str(self.label)+": "+str(self.content)+" tags: "+str(self.tags)
