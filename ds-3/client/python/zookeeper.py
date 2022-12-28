from kazoo.client import KazooClient


def register(zk: KazooClient, node_ip_addr, parent_node_ip_addr):
    # Create Root node
    if parent_node_ip_addr is None and not zk.exists(f'/{node_ip_addr}'):
        zk.create(f'/{node_ip_addr}', makepath=True)
        return

    # Find parent path
    parent_node_path = get_path_for_parent(zk, parent_node_ip_addr)

    # Create node after parent
    if parent_node_path is not None:
        zk.create(f'{parent_node_path}/{node_ip_addr}', makepath=True)


def get_path_for_parent(zk: KazooClient, parent_node_ip_addr):
    paths = ['/']

    while len(paths) > 0:
        curr_path = paths.pop()

        data, stat = zk.get(curr_path)

        if stat.children_count > 0:
            children = zk.get_children(curr_path)

            if parent_node_ip_addr in children:
                return f'{curr_path}/{parent_node_ip_addr}'

            for ip_addr in children:
                if curr_path == '/':
                    paths.append(f'/{ip_addr}')
                else:
                    paths.append(f'{curr_path}/{ip_addr}')
    return None
