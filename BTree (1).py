class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.children = []


class BTree:
    def __init__(self, t):
        self.root = BTreeNode()
        self.t = t

    def search(self, key, node=None):
        if node is None:
            node = self.root

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            return True

        if node.leaf:
            return False

        return self.search(key, node.children[i])

    def insert(self, key):
        if len(self.root.keys) == (2 * self.t) - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1

        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t) - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def split_child(self, parent, i):
        t = self.t
        child = parent.children[i]
        new_child = BTreeNode(leaf=child.leaf)

        parent.keys.insert(i, child.keys[t - 1])
        parent.children.insert(i + 1, new_child)

        new_child.keys = child.keys[t:2 * t - 1]
        child.keys = child.keys[0:t - 1]

        if not child.leaf:
            new_child.children = child.children[t:2 * t]
            child.children = child.children[0:t]

    def delete(self, key):
        if not self.root:
            return False

        return self._delete(self.root, key)

    def _delete(self, node, key):
        if key in node.keys:
            index = node.keys.index(key)
            if node.leaf:
                node.keys.remove(key)
            else:
                # Case 2a: Internal node and key is in an internal node
                if len(node.children[index].keys) >= self.t:
                    predecessor = self.get_predecessor(node, index)
                    node.keys[index] = predecessor
                    self._delete(node.children[index], predecessor)
                # Case 2b: Internal node and key is in a node with too few keys
                elif len(node.children[index + 1].keys) >= self.t:
                    successor = self.get_successor(node, index)
                    node.keys[index] = successor
                    self._delete(node.children[index + 1], successor)
                # Case 2c: Internal node and both the predecessor and successor nodes have minimum keys
                else:
                    self.merge(node, index)
                    self._delete(node.children[index], key)
            return True
        else:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1

            if node.leaf:
                return False

            # Case 1: Key is not in the node, but the child where it could be is at minimum capacity
            if len(node.children[i].keys) == self.t - 1:
                # Case 1a: If the left sibling has enough keys, borrow from it
                if i > 0 and len(node.children[i - 1].keys) >= self.t:
                    self.borrow_from_left_sibling(node, i)
                # Case 1b: If the right sibling has enough keys, borrow from it
                elif i < len(node.keys) and len(node.children[i + 1].keys) >= self.t:
                    self.borrow_from_right_sibling(node, i)
                # Case 1c: Merge the child with its sibling
                else:
                    if i < len(node.keys):
                        self.merge(node, i)
                    else:
                        self.merge(node, i - 1)
            return self._delete(node.children[i], key)

    def borrow_from_left_sibling(self, parent, index):
        child = parent.children[index]
        left_sibling = parent.children[index - 1]

        # Move key from parent down to child
        child.keys.insert(0, parent.keys[index - 1])
        if not child.leaf:
            child.children.insert(0, left_sibling.children.pop())

        # Move rightmost key from left sibling to parent
        parent.keys[index - 1] = left_sibling.keys.pop()

    def borrow_from_right_sibling(self, parent, index):
        child = parent.children[index]
        right_sibling = parent.children[index + 1]

        # Move key from parent down to child
        child.keys.append(parent.keys[index])
        if not child.leaf:
            child.children.append(right_sibling.children.pop(0))

        # Move leftmost key from right sibling to parent
        parent.keys[index] = right_sibling.keys.pop(0)

    def merge(self, parent, index):
        child = parent.children[index]
        sibling = parent.children[index + 1]

        # Move key from parent down to child
        child.keys.append(parent.keys[index])
        parent.keys.pop(index)

        # Move keys and children from sibling to child
        child.keys.extend(sibling.keys)
        child.children.extend(sibling.children)

        # Remove sibling from parent
        parent.children.pop(index + 1)

    def get_predecessor(self, node, index):
        current_node = node.children[index]
        while not current_node.leaf:
            current_node = current_node.children[-1]
        return current_node.keys[-1]

    def get_successor(self, node, index):
        current_node = node.children[index + 1]
        while not current_node.leaf:
            current_node = current_node.children[0]
        return current_node.keys[0]


# Example usage:
if __name__ == "__main__":
    b_tree = BTree(t=3)

    # Insertion
    b_tree.insert(10)
    b_tree.insert(20)
    b_tree.insert(5)
    b_tree.insert(6)
    b_tree.insert(12)
    b_tree.insert(30)
    b_tree.insert(7)
    b_tree.insert(17)

    print("Search for key 20:", b_tree.search(20))  # Output: True
    print("Search for key 25:", b_tree.search(25))  # Output: False

    # Deletion
    b_tree.delete(20)
    print("Search for key 20 after deletion:", b_tree.search(20))  # Output:
