import platform
import multiprocessing as mp
import random
import string

# define a example function
import time


def print_sysinfo():
    print('\nPython version  :', platform.python_version())
    print('compiler        :', platform.python_compiler())

    print('\nsystem     :', platform.system())
    print('release    :', platform.release())
    print('machine    :', platform.machine())
    print('processor  :', platform.processor())
    print('CPU count  :', mp.cpu_count())
    print('interpreter:', platform.architecture()[0])
    print('\n\n')


def rand_string(length, pos, output):
    """ Generates a random string of numbers, lower- and uppercase chars. """
    rand_str = ''.join(random.choice(
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits)
                       for i in range(length))
    output.put((pos, rand_str))


def cube(x):
    return x ** 3


if __name__ == '__main__':
    random.seed(123)
    start_t = time.time()
    output = mp.Queue()
    processes = [mp.Process(target=rand_string, args=(4, x, output)) for x in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    results = [output.get() for p in processes]
    print(results)
    print(time.time() - start_t)

    pool = mp.Pool(processes=4)
    results = results = pool.map(cube, range(1, 7))
    print(results)
    print_sysinfo()
