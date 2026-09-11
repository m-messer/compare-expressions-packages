"""Helpers for the tags carried by expression-tree nodes."""


def tag_rule_union(x, y):
    return x | y


def tag_rule_intersection(x, y):
    return x & y


def tag_transfer(node, rule=tag_rule_union):
    tags = set()
    if len(node.children) > 0:
        tags = set(node.children[0].tags)
        for child in node.children[1:]:
            tags = rule(tags, child.tags)
    return tags


def tag_removal(node, tag, rule=lambda x: True):
    if rule(node.tags) and tag in node.tags:
        node.tags.remove(tag)
    return node


def tag(node, tag=None, rule=lambda x: True):
    if tag is not None:
        if node.tags is None:
            node.tags = set()
        if rule(node.tags):
            node.tags.add(tag)
    return node


def tag_replace(node, old_tag, new_tag):
    if old_tag in node.tags:
        node = tag(node, new_tag)
        node = tag_removal(node, old_tag)
    return node
