
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import math
from timeit import default_timer

import numpy as np


def _import(*mod_name_parts):
    """"
    Import a module.

    Dirty replacement for missing importlib.import_module in py26.
    """
    return __import__('.'.join(mod_name_parts), None, None, '*')


def single_benchmark(proto, conn, amount, repeat=1):
    """
    Benchmark the specified protocol with the specified connection.

    :param str proto:
    :param str conn:
    :param int amount:
    :param int repeat:
    :returns: startup + transfer time
    :rtype: double
    """
    mod_proto = _import('ipctest.protocol', proto)
    mod_conn = _import('ipctest.connection', conn)
    start = default_timer()
    conn = mod_proto.spawn(mod_conn.Connection)
    for i in range(repeat):
        conn.send(amount)
        data = conn.recv()
    conn.close()
    end = default_timer()
    return end - start


def multiple_benchmarks(modes, sample_count, step_size):
    """
    Benchmark multiple protocol/connection modes.

    :param list modes:
    :param int sample_count:
    :param int step_size:
    """
    split_modes = [m.split(':', 1) for m in modes]
    sample_sizes = np.arange(sample_count) * step_size
    # Perform a dummy run, so all modules will be loaded. The purpose is to
    # prevent performance hits in the first (amount=0) benchmark:
    for proto, conn in split_modes:
        single_benchmark(proto, conn, 0)
    results = [[single_benchmark(proto, conn, amount)
                for proto, conn in split_modes]
               for amount in sample_sizes]
    amount_bytes = np.array([np.arange(a).nbytes for a in sample_sizes])
    return np.hstack((amount_bytes.reshape(-1, 1),
                      np.array(results)))


def fit_all(modes, data, file):
    """
    """
    print('#', 'mode', 'm [s/KB]', 'c [s]',  sep='\t', file=file)
    for i, k in enumerate(modes):
        m, c = _fit_linear(data[:,0] / 1000, data[:,i+1])
        print(k, m, c, 1/m/1000, file=file)


def _fit_linear(x, y):
    """
    Perform linear fit through x/y value pairs.

    :param numpy.ndarray x:
    :param numpy.ndarray y:
    :returns: slope m, offset c, such that y[i] ~= m*x[i] + c
    :rtype: tuple
    """
    A = np.array([x, np.ones_like(x)])
    return np.linalg.lstsq(A.T, y)[0]


def plot(modes, data, filename=None):
    """
    Plot figure.
    """
    from matplotlib import pyplot as plt
    figure = plt.figure()
    axes = figure.add_subplot(111)
    axes.set_xlabel('data size $x$ [KB]')
    axes.set_ylabel('time $t$ [s]')
    for i, k in enumerate(modes):
        axes.plot(data[:,0] / 1000, data[:,i+1], label=k)
    axes.legend(loc='upper left')
    if filename:
        figure.savefig(filename)
    else:
        plt.show()
    plt.close()

