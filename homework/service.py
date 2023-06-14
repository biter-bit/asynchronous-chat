import subprocess, ipaddress, tabulate

network_node = ['209.185.108.134']


def host_range_ping_tab(func):
    def wrapper(*args, **kwargs):
        colums = ['Reachable', 'Unreachable']
        result = func(*args, **kwargs)
        print(tabulate.tabulate(result, headers=colums))
    return wrapper


def host_ping(list_network_node):
    for i in list_network_node:
        ip = ipaddress.ip_address(i)
        p = subprocess.Popen(f'ping -c 1 {ip}', shell=True, stdout=subprocess.PIPE)
        code = p.wait()
        if code == 0:
            print(f'{i} - узел доступен')
        elif code == 1:
            print(f'{i} - узел недоступен')


@host_range_ping_tab
def host_range_ping(list_network_node):
    result_list = []
    for i in list_network_node:
        ip = str(ipaddress.ip_address(i)), str(ipaddress.ip_address(i) + 5)
        result_list.append(ip)
    return result_list


host_range_ping(network_node)