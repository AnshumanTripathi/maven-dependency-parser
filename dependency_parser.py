class Dependency:
    def __init__(self, dependency_fqn):
        names = dependency_fqn.split(":")
        self.group_name = names[0]
        self.artifact_name = names[1]
        self.type = names[2]
        self.version = names[3]
        if len(names) > 4:
            self.goal = names[4]


class Node:
    def __init__(self, dependency_name):
        self.dependency_name = self._sanitize_dependency(dependency_name)
        self.children = []
        self.parent = None
        self.level = 0

    def add_child(self, node):
        self._validate_node(node)
        node.parent = self
        node.level = self.level + 1
        self.children.append(node)

    def contains(self, node):
        self._validate_node(node)
        found = False
        if self.dependency_name == node.dependency_name:
            found = True
        else:
            for child in self.children:
                found = child.contains(node)
                if found:
                    break
        return found

    def get_child(self, node):
        self._validate_node(node)
        if self.dependency_name == node.dependency_name:
            return node
        else:
            for child in self.children:
                return child.get_child(node)

    def traverse(self):
        self._traverse_node(self)

    def _traverse_node(self, node):
        print node.dependency_name
        if len(node.children) == 0:
            return
        else:
            for child in node.children:
                self._traverse_node(child)

    def get_node(self, dependency):
        return self._get_node(self, dependency)

    def _get_node(self, node, dependency):
        found = None
        if node.dependency_name == dependency:
            found = node
        else:
            for child in node.children:
                found = self._get_node(child, dependency)
                if found is not None:
                    break
        return found

    def get_ancestors(self, dependency):
        node = self.get_node(dependency)
        return self._get_ancestors(node)

    def _get_ancestors(self, node, ancestors=[]):
        if node.parent is None:
            return ancestors
        else:
            ancestors.append(node.parent.dependency_name)
            return self._get_ancestors(node.parent, ancestors)

    def _validate_node(self, node):
        if self.__class__ != node.__class__:
            raise Exception('Only node type are allowed')

    @staticmethod
    def _sanitize_dependency(dependency_name):
        if "+-" in dependency_name:
            return dependency_name.split("+-")[1].strip()
        elif "\\-" in dependency_name:
            return dependency_name.split("\\-")[1].strip()
        else:
            return dependency_name.strip()


class TreeBuilder:
    def __init__(self, dependency_file):
        self.dependency_file = dependency_file
        self.root = self._get_root()

    def _get_root(self):
        with open(self.dependency_file, 'r') as f:
            return Node(f.readline().strip())

    @staticmethod
    def _compute_level(dependency):
        level = 1
        for sym in dependency:
            if sym == '|':
                level += 1
            elif sym == '+' or sym == '\\':
                break
        return level

    def build(self):
        with open(self.dependency_file, 'r') as f:
            lines = f.readlines()
            del lines[0]            # delete root node
        parent = self.root

        for line in lines:
            level = self._compute_level(line)
            child = Node(line)

            while parent.level >= level:
                parent = parent.parent

            parent.add_child(child)
            parent = child

        return self.root


node = TreeBuilder('test.txt').build()
# node.contains(Node('javax.xml.bind:jaxb-api:jar:2.3.0:compile'))
ancestors = node.get_ancestors('com.sun.jersey:jersey-core:jar:1.19.1:runtime')
for ancestor in ancestors:
    print Dependency(ancestor).__dict__



