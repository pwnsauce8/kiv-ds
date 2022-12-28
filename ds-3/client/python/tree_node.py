class Node:
    def __init__(self, ip, parent_ip):
        self.ip_parent = parent_ip
        self.left = None
        self.right = None
        self.ip_addr = ip

    def printTree(self, node, level=0):
        ret = ''
        if node is not None:
            ret += self.printTree(node.left, level + 1)
            ret += ' ' * 4 * level + '-> ' + str(node.ip_addr) + '\n'
            print(' ' * 4 * level + '-> ' + str(node.ip_addr), flush=True)
            ret += self.printTree(node.right, level + 1)
        return ret

    def inorder(self, node):
        """ Inorder traversal of a binary tree"""
        if not node:
            return

        self.inorder(node.left)
        print(node.key, end=" ")
        self.inorder(node.right)

    def insert(self, key):
        """function to insert element in binary tree """
        if not self:
            root = Node(key, None)
            return
        q = [self]

        # Do level order traversal until we find
        # an empty place.
        while len(q):
            temp = q[0]
            q.pop(0)

            if not temp.left:
                temp.left = Node(key, temp.ip_addr)
                return temp.ip_addr
            else:
                q.append(temp.left)

            if not temp.right:
                temp.right = Node(key, temp.ip_addr)
                return temp.ip_addr
            else:
                q.append(temp.right)
