"""
Usage:
    benchmark.py --auto=<dir>
    benchmark.py [options] <mode>...
    benchmark.py --help

Options:
    -a <dir>, --auto=<dir>          Chose filenames automatically in <dir>
    -p <file>, --plot=<file>        Save plot
    -d <file>, --data=<file>        Save raw benchmark data
    -f <file>, --fit=<file>         Save fit results
    -c <count>, --count=<count>     Set number of samples
    -s <step>, --step=<step>        Set step size
"""

from __future__ import absolute_import

import os
import sys

import numpy as np
from docopt import docopt

from ipctest import fit_all, plot, multiple_benchmarks


def demo_settings(path):
    """Get default settings for some of the arguments."""
    pyver = '-'.join(map(str, sys.version_info))
    prefix = os.path.join(path, '_'.join((pyver, sys.platform)))
    return {
        '--fit': prefix + '.fit',
        '--plot': prefix + '.pdf',
        '--data': prefix + '.txt',
        '<mode>': [
            #'inherit_duplex:pickle',   # (1), (2)
            'inherit_unidir:pickle',
            #'inherit_unidir:pipe',     # (3)
            'inherit_duplex:pipe',
            'stdio:pickle',
            'socket:sockpipe',
            #'socket:pickle',           # (4), (5)
            #'multiprocessing:pipe',    # (6)
        ]
    }
    # (1) problems on py34, don't know why
    # (2) Pipe() returns a named pipe with specific flags, incompatible with
    #     standard python file IO
    # (3) related to (2): PipeConnection requires named pipe with specific
    #     flags, while we are using _winapi.CreatePipe here
    # (4) uninvestigated problems on win
    # (5) uninvestigated problems on py34
    # (6) there is no problem here, just that multiprocessing is not really an
    #     option and the plot looks nicer without it.
    #     (since all other methods have large offsets on linux)


def main(argv=None):

    """Execute the main script."""

    args = docopt(__doc__, argv)

    if args['--auto']:
        defaults = demo_settings(args['--auto'])
        for k, v in defaults.items():
            if not args.get(k):
                args[k] = v

    modes = args['<mode>']
    sample_count = int(args['--count'] or 100)
    step_size = int(args['--step'] or 10000)

    fit_file = args['--fit']
    plot_file = args['--plot']
    data_file = args['--data']

    data = multiple_benchmarks(modes, sample_count, step_size)

    if data_file:
        np.savetxt(data_file, data)

    if fit_file:
        with open(fit_file, 'w') as f:
            fit_all(modes, data, f)

    if plot_file:
        if plot_file == '-':
            plot(modes, data)
        else:
            plot(modes, data, plot_file)


if __name__ == '__main__':
    main()
