#!/usr/bin/env python

import os
import subprocess
import argparse

from utils import *
from parser import *

RESULTS = 'results'

EXPERIMENTS = [
    ('1x1', 'cpu'),   
    #('2x1', 'cpu'), ('1x2', 'cpu'),
    #('2x2', 'cpu'), ('4x1', 'cpu'), ('1x4', 'cpu'),
    #('4x2', 'cpu'), ('8x1', 'cpu'), ('1x8', 'cpu'),
    #('4x4', 'cpu'), ('8x2', 'cpu'), ('2x8', 'cpu'),
    #('6x4', 'cpu'), ('4x6', 'cpu'),
    ('1x1', 'gpu'),
    ('2x1', 'gpu'), ('1x2', 'gpu'),
    ('2x2', 'gpu'), ('4x1', 'gpu'), ('1x4', 'gpu'),
    ('4x2', 'gpu'), ('8x1', 'gpu'), ('1x8', 'gpu'),
]

# Change maximum number of iterations
MAX_ITER = 10

# Rank experiment list 
# These experiments can take a very long time, 
# therefore filtering is needed

RANK_EXPERIMENTS = [
    ('ArrayExpress', '4x1', 'gpu'),
    ('TCGA-BRCA', '1x4', 'gpu'),
    ('fetus', '2x2', 'gpu'),
    ('retina', '2x2', 'gpu'),
    ('cochlea', '2x2', 'gpu'),
]

SPARSE_MAP = {'ArrayExpress': False, 'TCGA-BRCA': False, 
    'fetus': True, 'retina': False, 'cochlea': False}

def process(cmd):
    p = subprocess.Popen(cmd.split(' '), stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

def run_batch(dataset, blocks='1x1', context='gpu', method='nmtf_long', 
    sparse='dense', transfer=True, balanced='balanced', k=20):
    data_file = to_path(RESULTS, '%s.csv' % dataset)
    
    data = []
    sp = ''
    orthogonal = ''
    g = ''
    bl = ''
    FRANK = k
    
    if sparse == 'sparse':
        sp = ' -s'
        if balanced == 'imbalanced':
            bl = ' -m'
    
    if context == 'gpu':
        g = ' -g'
    if method == 'nmtf_ding':
        orthogonal = ' -o'

    tr = ''
    if not transfer:
        tr = ' --no-transfer'
    cmd = 'crow%s%s%s -b %s -i %d -k1 %d%s%s %s.coo' % (sp, g, 
        orthogonal, blocks, MAX_ITER, FRANK, tr, bl, dataset)
    t = process(cmd)
    if t == None:
        print "Warning: timing %s failed" % cmd
        return None
    if transfer:
        print "Dataset %s, %s, %s, time: %s" % (dataset, blocks, context, t)
    else:
        print "Dataset %s, %s, %s, time: %s (communication disabled)" % (dataset, blocks, context, t)
    columns = ['method', 'context', 'blocks', 'k', 'balanced', 'sparse', 'sync', 'time']
    data.append({'method': 'nmtf_long', 'context': context, 
        'k': FRANK, 'blocks': blocks, 'sparse': sparse,
        'balanced': balanced, 'sync': transfer, 'time': t})
    save_csv_dict(data_file, data, columns=columns, append=True)

def benchmark(argv, method, update=True, comm=False, imb=False, rank=False):
    all_data = read_datasets2(argv)
    
    for dataset in argv:
        print dataset
        for block, context in EXPERIMENTS:
            sparse = 'dense'
            if SPARSE_MAP[dataset] == True:
                sparse = 'sparse'
            
            config = {'context': context, 'blocks': block, 'sparse': sparse, 'method': method}
            exists = compare_configs(all_data[dataset], config)
            if exists == False:
                run_batch(dataset, blocks=block, context=context, method=method, sparse=sparse)
            
            if comm == True:
                config = {'context': context, 'blocks': block, 'sparse': sparse, 'method': method, 'sync': False}
                exists = compare_configs(all_data[dataset], config)
                if exists == False:
                    run_batch(dataset, blocks=block, context=context, method=method, sparse=sparse, transfer=False)
    
    if imb == True:
        for dataset in argv:
            for block, context in EXPERIMENTS:
                sparse = 'sparse'
                config = {'context': context, 'blocks': block, 'method': method, 'sparse': sparse, 'balanced': 'balanced'}
                exists = compare_configs(all_data[dataset], config)
                if exists == False:
                    run_batch(dataset, blocks=block, context=context, method=method, sparse=sparse)
                
                balanced = 'imbalanced'
                config = {'context': context, 'blocks': block, 'method': method, 'sparse': sparse, 'balanced': balanced}
                exists = compare_configs(all_data[dataset], config)
                if exists == False:
                    run_batch(dataset, blocks=block, context=context, method=method, sparse=sparse, balanced=balanced)
    
    if rank == True:
        for dataset, block, context in RANK_EXPERIMENTS:
            sparse = 'dense'
            if SPARSE_MAP[dataset] == True:
                sparse = 'sparse'
            for k in range(10, 110, 10):
                config = {'context': context, 'blocks': block, 'sparse': sparse, 'method': method, 'k': str(k)}
                exists = compare_configs(all_data[dataset], config)
                if exists == False:
                    run_batch(dataset, blocks=block, context=context, method=method, sparse=sparse, k=k)
                

def main():
    parser = argparse.ArgumentParser(version='0.1', description='crow-plot')
    parser.add_argument("-c", "--communication", action="store_true", help="Calculate also communication overhead")
    parser.add_argument("-i", "--imbalanced", action="store_true", help="Calculate also imbalanced speedup")
    parser.add_argument("-m", "--method", help="Choose between nmtf_long and nmtf_ding")
    parser.add_argument("-r", "--rank", action="store_true", help="Calculate for different factorization ranks")
    parser.add_argument("-f", "--force", action="store_true", help="Re-run and overwrite results")
    parser.add_argument("-u", "--update", action="store_true", help="Do not re-run if results exist")
    
    parser.add_argument('args', nargs='*', help='Other args')
    args = parser.parse_args()
    
    argv = args.args
    if len(argv) == 0:
        raise Exception("No datasets selected")
    
    method = 'nmtf_long'
    if args.method:
        method = args.method
    
    update = args.update
    notforce = not args.force
    
    ensure_dir(RESULTS)
    benchmark(argv, method, update=notforce, comm=args.communication, imb=args.imbalanced, rank=args.rank)
    
if __name__ == '__main__':
    main()
