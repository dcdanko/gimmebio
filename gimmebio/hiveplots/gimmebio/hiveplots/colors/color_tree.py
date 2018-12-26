
class ColorNode:

    def __init__(self, label, parent, value=0):
        self.label = label
        self.parent = parent
        if self.parent is not None:
            self.parent.add_child(self)
        self.children = set()
        self.value = value
        self.color = None

    def add_child(self, child):
        self.children.add(child)

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.children) == 0

    def childless_valueless_copy(self):
        return ColorNode(self.label, self.parent)

    def setColor(self, cmap, scaler, start, end):
        mycolor = (start + end) / 2
        mycolor = cmap(mycolor)
        self.color = mycolor
        childvals = [scaler * child.value for child in self.children]
        slop = (end - start) - sum(childvals)
        slopIncrement = slop / (len(self.children) + 5)
        newstart = start + 2 * slopIncrement
        for child in self.children:
            childStart = newstart + slopIncrement
            childEnd = childStart + scaler * child.value
            child.setColor(cmap, scaler, childStart, childEnd)
            newstart = childEnd


class MasterColorTree:

    def __init__(self):
        self.root = ColorNode('root', None)
        self.nodes = {'root': self.root}

    def add_node(self, label, value):
        tkns = label.split('|')
        if len(tkns) > 1:
            parentLabel = tkns[-2]
        elif len(tkns) ==1:
            parentLabel = 'root'
        nodeLabel = tkns[-1]
        parent = self.nodes[parentLabel]
        try:
            node = self.nodes[nodeLabel]
        except KeyError:
            node = ColorNode(nodeLabel, parent)
            self.nodes[nodeLabel] = node
        node.value += value
        return node

    def color_map(self, cmap, labels=None, spacer=1.1):
        if labels is None:
            labels = {leaf.label for leaf in self.get_leafs()}
        leafs = {self.nodes[label.split('|')[-1]] for label in labels}
        root = build_tree_from_leafs(leafs, spacer)
        scaler = 1.0 / root.value
        root.setColor(cmap, scaler, 0, 1)
        leafCols = {leaf.label: leaf.color for leaf in leafs}
        return leafCols

    def get_leafs(self):
        return get_leafs(self.root)


def get_leafs(node):
    leafs = []
    for child in node.children:
        if child.is_leaf():
            leafs.append(child)
        else:
            leafs += get_leafs(child)
    return leafs


def build_tree_from_leafs(leafs, spacer):
    parents = {leaf.parent for leaf in leafs if leaf.parent is not None}
    newparents = {parent.label: parent.childless_valueless_copy()
                  for parent in parents}
    for leaf in leafs:
        newparent = newparents[leaf.parent.label]
        newparent.add_child(leaf)
        newparent.value += leaf.value

    newparents = [newparent for newparent in newparents.values()]
    for newparent in newparents:
        newparent.value *= spacer

    if len(newparents) == 1:
        return newparents[0]
    notroot = [parent for parent in newparents if not parent.is_root()]
    return build_tree_from_leafs(notroot, spacer)
