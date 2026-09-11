"""Helpers for the tags carried by expression-tree nodes."""


def union_rule(x, y):
    return x | y


def intersection_rule(x, y):
    return x & y


def inherit_tags(node, rule=union_rule):
    tags = set()
    if len(node.children) > 0:
        tags = set(node.children[0].tags)
        for child in node.children[1:]:
            tags = rule(tags, child.tags)
    return tags


def remove_tag(node, tag, rule=lambda x: True):
    if rule(node.tags) and tag in node.tags:
        node.tags.remove(tag)
    return node


def add_tag(node, tag=None, rule=lambda x: True):
    if tag is not None:
        if node.tags is None:
            node.tags = set()
        if rule(node.tags):
            node.tags.add(tag)
    return node


def replace_tag(node, old_tag, new_tag):
    if old_tag in node.tags:
        node = add_tag(node, new_tag)
        node = remove_tag(node, old_tag)
    return node
