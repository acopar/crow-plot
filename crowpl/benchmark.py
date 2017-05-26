#!/usr/bin/env python

import os
import subprocess
import argparse

from utils import *

RESULTS = 'results'

EXPERIMENTS = [
    ('1x1', 'cpu'),   
    ('1x1', 'gpu'),
    ('2x1', 'gpu'),
    ('1x2', 'gpu'),
    ('2x2', 'gpu'),
    ('4x1', 'gpu'),
    ('1x4', 'gpu'),
    #('4x2', 'gpu'),
    #('8x1', 'gpu'),
    #('1x8', 'gpu'),
]

SPARSE_MAP = {'ArrayExpress': False, 'TCGA-BRCA': False, 
    'fetus': True, 'retina': False, 'cochlea': False}

def process(cmd):
    p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        print err
        raise Exception("Error output detected")
    t = None
    for line in out.split('\n'):
        x = line.strip()
        if 'Average iteration time' in x:
            x = x.replace('Average iteration time', '')
            x = x.replace('[', '').replace(']', '').replace(':', '')
            x = x.strip()
            t = float(x)
    
    return t

def run_batch(dataset, blocks='1x1', context='gpu', method='nmtf_long', transfer=True):
    data_file = to_path(RESULTS, '%s.csv' % dataset)
    
    data = []
    sparse = ''
    orthogonal = ''
    g = ''
    MAX_ITER = 10
    FRANK = 20
    
    if SPARSE_MAP[dataset] == True:
        sparse = ' -s'
    if context == 'gpu':
        g = ' -g'
    if method == 'nmtf_ding':
        orthogonal = ' -o'
    
    tr = ''
    if not transfer:
        tr = ' --no-transfer'
    cmd = 'crow%s%s%s -b %s -i %d -k1 %d%s %s.coo' % (sparse, g, 
        orthogonal, blocks, MAX_ITER, FRANK, tr, dataset)
    t = process(cmd)
    if t == None:
        print "Warning: timing %s failed" % cmd
        return None
    if transfer:
        print "Dataset %s, %s, %s, time: %s" % (dataset, blocks, context, t)
    else:
        print "Dataset %s, %s, %s, time: %s (communication disabled)" % (dataset, blocks, context, t)
    columns = ['method', 'context', 'blocks', 'balanced', 'time']
    data.append({'method': 'nmtf_long', 'context': context, 'balanced': 'balanced',
        'blocks': blocks, 'time': t})
    save_csv_dict(data_file, data, columns=columns, append=True)
        
def benchmark(argv, method):
    data_list = ['ArrayExpress', 'TCGA-BRCA', 'fetus', 'retina', 'cochlea']
    
    for dataset in argv:
        for block, context in EXPERIMENTS:
            run_batch(dataset, blocks=block, context=context, method=method)
    
    for dataset in argv:
        for block, context in EXPERIMENTS:
            run_batch(dataset, blocks=block, context=context, method=method, transfer=False)


def main():
    parser = argparse.ArgumentParser(version='0.1', description='crow-plot')
    parser.add_argument("-m", "--method", help="Choose between nmtf_long and nmtf_ding")
    parser.add_argument("-a", "--action", default='speedup', help="Pick: benchmark, speedup, k, balance, efficiency, communication")
    
    parser.add_argument('args', nargs='*', help='Other args')
    args = parser.parse_args()
    
    argv = args.args
    if len(argv) == 0:
        raise Exception("No datasets selected")
    
    method = 'nmtf_long'
    if args.method:
        method = args.method
    
    ensure_dir(RESULTS)
    benchmark(argv, method)
    
if __name__ == '__main__':
    main()
