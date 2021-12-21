import sys

import mga

DEFAULT_TELEPORT_PROB = 0.25

if __name__ == '__main__':

    argc = len(sys.argv)

    if argc == 1:
        teleport_prob = DEFAULT_TELEPORT_PROB
        verbose = False
    elif argc == 2:
        if '-v' in sys.argv[1:]:
            verbose = True
            teleport_prob = DEFAULT_TELEPORT_PROB
        else:
            verbose = False
            teleport_prob = float(sys.argv[1])
    elif argc == 3:
        verbose = '-v' in sys.argv[1:]
        teleport_prob = float(sys.argv[1])
    else:
        print(f'Usage: {sys.argv[0]} [<teleport_probability>] [-v]', file=sys.stderr)
        sys.exit(1)

    print(f'Teleport probability: {teleport_prob}')
    print(f'Verbose: {verbose}')

    df = mga.pagerank(base_dir='./', teleport_prob=teleport_prob, disable_progress_bar=not verbose)
    df.to_csv('movies_pr.csv')
