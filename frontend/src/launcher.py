import subprocess, multiprocessing, sys


def client_start():
    subprocess.Popen('python client_ui.py', shell=True).wait()


if __name__ == '__main__':
    param = sys.argv
    count = 1
    for i in param:
        if i == '-c':
            count = int(param[param.index(i) + 1])
    for i in range(count):
        multiprocessing.Process(target=client_start, name=f'prc-{i}').start()
