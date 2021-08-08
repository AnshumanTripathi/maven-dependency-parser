import argparse

class Dependency:
    """
    An object that represents a dependency.
    """
    def __init__(self, dependency_fqn: str):
        names = dependency_fqn.split(":")
        self.group_name = names[0]
        self.artifact_name = names[1]
        self.type = names[2]
        self.version = names[3]
        if len(names) > 4:
            self.goal = names[4]


class Node:
    """
    A node in the dependency tree.
    """
    def __init__(self, dependency_name: str, level: int = 0):
        self.dependency_name = self._sanitize_dependency(dependency_name)
        self.children = []
        self.parent = None
        self.level = 0

    """
    Add a dependency to the tree.
    @param node: The node to add.
    """
    def add_child(self, node: 'Node'):
        self._validate_node(node)
        node.parent = self
        node.level = self.level + 1
        self.children.append(node)

    """
    Check if the node is present in the dependency tree.
    @param node: The node to check.
    """
    def contains(self, node: 'Node'):
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

    """
    Get the immidiate child of the node.
    @param node: The node to get the immidiate child of.
    """
    def get_child(self, node: 'Node'):
        self._validate_node(node)
        if self.dependency_name == node.dependency_name:
            return node
        else:
            for child in self.children:
                return child.get_child(node)

    """
    Traverse the tree recursively and print the tree.
    """
    def traverse(self):
        self._traverse_node(self)

    def _traverse_node(self, node: 'Node'):
        print(node.dependency_name)
        if len(node.children) == 0:
            return
        else:
            for child in node.children:
                self._traverse_node(child)

    """
    Get the node object from the given depedency.
    @param dependency: The dependency to get the node from.
    """
    def get_node(self, dependency: str) -> 'Node':
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

    """
    Get all the anecsors of the given dependency.
    @param dependency: The dependency to get the anecsors of.
    """
    def get_ancestors(self, dependency: str) -> list:
        node = self.get_node(dependency)
        return self._get_ancestors(node)

    def _get_ancestors(self, node, ancestors=[]):
        if node.parent is None:
            return ancestors
        else:
            ancestors.append(node.parent.dependency_name)
            return self._get_ancestors(node.parent, ancestors)

    """
    Validate that only node type are allowed.
    """
    def _validate_node(self, node):
        if self.__class__ != node.__class__:
            raise Exception('Only node type are allowed')

    """
    Sanitize the dependency name.
    @param dependency: The dependency to sanitize.
    """
    @staticmethod
    def _sanitize_dependency(dependency_name: str) -> str:
        if "+-" in dependency_name:
            return dependency_name.split("+-")[1].strip()
        elif "\\-" in dependency_name:
            return dependency_name.split("\\-")[1].strip()
        else:
            return dependency_name.strip()


class TreeBuilder:
    """
    Build a tree from the given dependency file.
    @param dependency_file: The file to build the tree from.
    """
    def __init__(self, dependency_file: str):
        self.dependency_file = dependency_file
        self.root = self._get_root()

    def _get_root(self):
        with open(self.dependency_file, 'r') as f:
            return Node(f.readline().strip())

    """
    Compute the level of the given line.
    """
    @staticmethod
    def _compute_level(dependency: str):
        level = 1
        for sym in dependency:
            if sym == '|':
                level += 1
            elif sym == '+' or sym == '\\':
                break
        return level

    """
    Build a tree from the given dependency file.
    """
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


"""
Parses the dependency file and returns a list of ancestors of the given dependency
@param dependency_file: the file containing the dependencies created from `mvn dependency:tree`
@param dependency: the dependency to find ancestors for
@return: a list of ancestors of the given dependency
"""
def parse(dependency_file: str, dependency: str) -> list: 
    node = TreeBuilder(dependency_file).build()
    ancestors = node.get_ancestors(dependency)
    return ancestors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dependency tree builder')
    parser.add_argument('-f', '--file', help='Dependency file', required=False)
    parser.add_argument('-d', '--dependency', help='Dependency name', required=True)
    args = parser.parse_args()
    ancestors = parse(args.file, args.dependency)    
    for ancestor in ancestors:
        print(Dependency(ancestor).__dict__)

