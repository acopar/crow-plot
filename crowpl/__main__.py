#!/usr/bin/env python

import os
import sys
import subprocess
import argparse
import numpy as np
import pandas as pd

from utils import *
import visualize

IMG = 'img'
RESULTS = 'results'

def cmp_configs(x, y):
    equal = True
    for key in y:
        if key not in x:
            continue
        if x[key] != str(y[key]):
            equal = False
    return equal

def from_template(x, y):
    dct = {key: value for key, value in x.items()}
    for key in y:
        dct[key] = y[key]
    return dct

def times_to_tuple(times_string):
    n, m = times_string.split('x')
    return '(%s, %s)' % (n, m)

def block_to_rank(block_string):
    n, m = block_string.split('x')
    p = int(n) * int(m)
    return p

def get_configlist(use_context, use_blockconfig):
    selected_configs = []
    for con in use_context:
        for block in use_blockconfig:
            selected_configs.append('%s %s' % (con, block))
    return selected_configs

def context_to_context(c):
    if c in ['gpu', 'hpu']:
        return 'gpu'
    return 'cpu'

def context_to_sync(c):
    if c in ['cpu', 'gpu']:
        return True
    return False

def read_wrapper(argv, method='nmtf_long', task='speedup', context='cpu', label='4', k='20', max_iter=100):
    data_list = argv
    if len(argv) == 0:
        print 'No datasets specified'
        return
    
    block_map = {
        'ArrayExpress': {1: '1x1', 2: '2x1', 4: '4x1', 8: '8x1'},
        'TCGA-BRCA': {1: '1x1', 2: '1x2', 4: '1x4', 8: '1x8'},
        'fetus': {1: '1x1', 2: '2x1', 4: '2x2', 8: '4x2'},
        'retina': {1: '1x1', 2: '2x1', 4: '2x2', 8: '4x2'},
        'cochlea': {1: '1x1', 2: '2x1', 4: '2x2', 8: '4x2'}
    }

    use_blockconfig = ['1x1', '2x1', '1x2', '4x1', '2x2', '1x4']

    selected_configs = None
    all_data = None
    
    if task == 'speedup':
        selected_configs = ['cpu 1x1', 'gpu 1x1', 'gpu 2x1', 'gpu 1x2', 'gpu 4x1', 
            'gpu 2x2', 'gpu 1x4']
        template = {'context': 'cpu', 'method': method, 'balanced': 'balanced', 
            'sync': True, 'k': k, 'max_iter': max_iter, 'blocks': '1x1'}
        configs = {key: {'context': key.split(' ')[0], 'blocks': key.split(' ')[1]} for key in selected_configs}

        conf_dict = {c: from_template(template, configs[c]) for c in selected_configs}
        all_data = read_datasets(data_list, conf_dict)

    elif task == 'efficiency':
        use_context = ['cpu', 'gpu', 'epu', 'hpu']
        
        selected_configs = get_configlist(use_context, use_blockconfig)
        template = {'context': 'cpu', 'method': method, 'balanced': 'balanced', 
            'sync': True, 'k': k, 'max_iter': max_iter, 'blocks': '1x1'}
        configs = {key: {'context': context_to_context(key.split(' ')[0]), 
            'blocks': key.split(' ')[1], 'sync': context_to_sync(key.split(' ')[0])} 
            for key in selected_configs}

        conf_dict = {c: from_template(template, configs[c]) for c in selected_configs}
        all_data = read_datasets(data_list, conf_dict)
    
    elif task == 'transfer':
        use_context = ['gpu', 'hpu']
        if context == 'cpu':
            use_context = ['cpu', 'epu']
        
        selected_configs = get_configlist(use_context, use_blockconfig)
        template = {'context': 'gpu', 'method': method, 'balanced': 'balanced', 
            'sync': True, 'k': k, 'max_iter': max_iter, 'blocks': '1x1'}
        configs = {key: {'context': context_to_context(key.split(' ')[0]), 
            'blocks': key.split(' ')[1], 'sync': context_to_sync(key.split(' ')[0])} for key in selected_configs}
        
        conf_dict = {c: from_template(template, configs[c]) for c in selected_configs}
        all_data = read_datasets(data_list, conf_dict)
    elif task == 'best_speedup':
        if context == 'gpu':
            selected_configs = ['cpu 1', 'gpu 1', 'gpu 2', 'gpu 4']
        else:
            selected_configs = ['cpu 1', 'cpu 2', 'cpu 4']
        template = {'context': 'cpu', 'method': method, 'balanced': 'balanced', 
            'sync': True, 'k': k, 'max_iter': max_iter, 'blocks': '1x1'}
        configs = {
            'cpu 1': {'context': 'cpu', 'blocks': '1x1'},
            'cpu 2': {'context': 'cpu', 'blocks': '2x1'},
            'cpu 4': {'context': 'cpu', 'blocks': '4x1'},
            'gpu 1': {'context': 'gpu', 'blocks': '1x1'},
            'gpu 2': {'context': 'gpu', 'blocks': '2x1'},
            'gpu 4': {'context': 'gpu', 'blocks': '4x1'}
        }
        
        conf_dict = {c: from_template(template, configs[c]) for c in selected_configs}
        all_data = read_datasets(data_list, conf_dict, block_map=block_map)
    elif task == 'balance':
        selected_configs = ['balanced 2x1', 'imbalanced 2x1', 'balanced 1x2', 'imbalanced 1x2', 
            'balanced 4x1', 'imbalanced 4x1', 'balanced 2x2', 'imbalanced 2x2', 'balanced 1x4', 'imbalanced 1x4']
        
        template = {'context': context, 'method': method, 'sparse': 'sparse', 
            'balanced': 'balanced', 'k': k, 'max_iter': max_iter, 'blocks': '2x2'}
        configs = {
            'balanced 4x1': {'balanced': 'imbalanced', 'blocks': '4x1'},
            'imbalanced 4x1': {'balanced': 'balanced', 'blocks': '4x1'},
            'balanced 2x2': {'balanced': 'imbalanced', 'blocks': '2x2'}, 
            'imbalanced 2x2': {'balanced': 'balanced', 'blocks': '2x2'},
            'balanced 1x4': {'balanced': 'imbalanced', 'blocks': '1x4'},
            'imbalanced 1x4': {'balanced': 'balanced', 'blocks': '1x4'},
            'balanced 2x1': {'balanced': 'imbalanced', 'blocks': '2x1'}, 
            'imbalanced 2x1': {'balanced': 'balanced', 'blocks': '2x1'},
            'balanced 1x2': {'balanced': 'imbalanced', 'blocks': '1x2'}, 
            'imbalanced 1x2': {'balanced': 'balanced', 'blocks': '1x2'}
        }
        
        conf_dict = {c: from_template(template, configs[c]) for c in selected_configs}
        all_data = read_datasets(data_list, conf_dict)
    elif task == 'k':
        template = {'context': context, 'method': method, 'balanced': 'balanced', 
            'max_iter': max_iter, 'blocks': '2x2'}
        selected_configs = list(range(10, 160, 10))
        configs = {key: {'k': '%d' % key} for key in selected_configs}
        
        conf_dict = {c: from_template(template, configs[c]) for c in selected_configs}
        all_data = read_datasets(data_list, conf_dict, block_map=block_map)
    else:
        raise Exception("Invalid task: %s" % task)
    
    return all_data

def read_datasets(datasets, configs, block_map=None, sparse_map=None):
    all_data = {}
    dataset_blocks = None
    dataset_sparse = None
    
    for dataname in datasets:
        if block_map:
            dataset_blocks = block_map[dataname]
        all_data[dataname] = {}
        
        index_file = to_path(RESULTS, '%s.csv' % dataname)
        
        data = load_csv_dict(index_file)
        if not data:
            print 'Warning: File not found %s' % index_file
            continue
        
        for d in data:
            blocks = d['blocks']
            blocks = [int(b) for b in blocks.split('x')]
            h = float(d['time'])
            
            add = None
            
            for c in configs:
                con = configs[c]
                con = {key: value for key, value in con.items()}
                if dataset_blocks:
                    bl = con['blocks']
                    blocks2 = [int(b) for b in bl.split('x')]
                    rank = blocks2[0]*blocks2[1]
                    con['blocks'] = dataset_blocks[rank]
                
                if cmp_configs(d, con):
                    add = c
            
            if add:
                if add in all_data[dataname]:
                    all_data[dataname][add].append(h)
                else:
                    all_data[dataname][add] = [h]
        if len(all_data[dataname]) == 0:
            print 'No data matched for %s' % dataname
    return all_data

def speedup_frame(data, task='best', labels={'x': 'Dataset', 'y': 'Speedup', 'z': 'Blocks'}):
    divider = None
    if task == 'balance':
        pairs = [('imbalanced 2x1', 'balanced 2x1'), ('imbalanced 1x2', 'balanced 1x2'),
        ('imbalanced 4x1', 'balanced 4x1'), ('imbalanced 2x2', 'balanced 2x2'), ('imbalanced 1x4', 'balanced 1x4')]
    elif task == 'best':
        pairs = [('cpu 1', 'gpu 1'), ('cpu 1', 'gpu 2'), ('cpu 1', 'gpu 4')]
    elif task == 'best cpu':
        pairs = [('cpu 1', 'cpu 1'), ('cpu 1', 'cpu 2'), ('cpu 1', 'cpu 4')]
    elif task == 'speedup':
        pairs = [('cpu 1x1', 'gpu 1x1'), ('cpu 1x1', 'gpu 2x1'), ('cpu 1x1', 'gpu 1x2'), 
            ('cpu 1x1', 'gpu 4x1'), ('cpu 1x1', 'gpu 2x2'), ('cpu 1x1', 'gpu 1x4')]
    elif 'efficiency' in task:
        context = task.split(' ')[1]
        pairs = []
        divider = {}
        for blocks in ['1x1', '2x1', '1x2', '4x1', '2x2', '1x4']:
            pairs.append(('%s 1x1' % context, '%s %s' % (context, blocks)))
            divider['%s %s' % (context, blocks)] = block_to_rank(blocks)
    if 'transfer' in task:
        task_, context, stage = task.split(' ')
        if stage == 'stage2':
            if context == 'cpu':
                context = 'epu'
            if context == 'gpu':
                context = 'hpu'
        pairs = []
        divider = {}
        for blocks in ['1x1', '2x1', '1x2', '4x1', '2x2', '1x4']:
            pairs.append(('%s 1x1' % context, '%s %s' % (context, blocks)))
            divider['%s %s' % (context, blocks)] = block_to_rank(blocks)
    
    frame = []
    for key in data:
        label = key
        tmp = data[key]
        for p in pairs:
            if not (p[0] in tmp and p[1] in tmp):
                continue
            t0 = np.mean(tmp[p[0]])
            for t1 in tmp[p[1]]:#[0]:
                speedup = t0 / t1
                if divider != None:
                    speedup = speedup / divider[p[1]]
                block = p[1].split(' ')[1]
                frame.append([key, speedup, block])
    
    if len(frame) == 0:
        print "Warning: Missing data, task: %s" % task
        return None
    
    x, y, z = labels['x'], labels['y'], labels['z']
    df = pd.DataFrame({x: [i[0] for i in frame], y: [i[1] for i in frame], z: [i[2] for i in frame]})
    return df

def rank_frame(data):
    frame = []
    for key in data:
        label = key
        
        tmp = data[key]
        for k in tmp.keys():
            for runtime in tmp[k]:
                frame.append([key, k, runtime])
    
    if len(frame) == 0:
        raise Exception("Missing data")
    df = pd.DataFrame({'Dataset': [i[0] for i in frame], 'Factorization rank': [i[1] for i in frame], 'Iteration time [s]': [i[2] for i in frame]})
    return df

def order_frame(df, order=None):
    if order:
        frames = []
        for d in order:
            frames.append(df[df['Dataset'] == d])
        df = pd.concat(frames)

    for i in df.index:
        df.set_value(i, 'Dataset', df.ix[i]['Dataset'].replace('-dense', ''))
        df.set_value(i, 'Dataset', df.ix[i]['Dataset'].replace('ArrayExpress', 'E-TABM-185'))
        df.set_value(i, 'Dataset', df.ix[i]['Dataset'].replace('fetus', 'Fetus'))
        df.set_value(i, 'Dataset', df.ix[i]['Dataset'].replace('retina', 'Retina'))
        df.set_value(i, 'Dataset', df.ix[i]['Dataset'].replace('cochlea', 'Cochlea'))
    return df

def line_plotter(data, img_file, label='gpu', order=None):
    df = rank_frame(data)
    df = order_frame(df, order=order)
    labels = {'x': 'Factorization rank', 'y': 'Iteration time [s]', 'z': 'Dataset'}
    visualize.lineplot(df, filename=img_file, labels=labels, x=labels['x'], y=labels['y'], z='Dataset')
    #, skipxlabels=10, xlabelrange=150)

def bar_plot(data, img_file, label='speedup', k='20', order=None):
    labels = {'x': 'Dataset', 'y': 'Speedup', 'z': 'Partitioning'}
    if 'balance' in label:
        labels['y'] = 'Speedup of balanced vs. imbalanced partitioning'
    if 'best' in label:
        labels['z'] = 'Processing Units'
    if 'efficiency' in label:
        labels['y'] = 'Efficiency'
    if 'communication' in label:
        labels['y'] = 'Communication overhead'
    
    df = speedup_frame(data, task=label, labels=labels)
    if df is None:
        return None
    df = order_frame(df, order=order)
    visualize.barplot(df, filename=img_file, labels=labels, x=labels['x'], y=labels['y'], z=labels['z'])

def multi_plot(data, img_file, label='speedup', k='20', order=None):
    labels = {'x': 'Dataset', 'y': 'Efficiency', 'z': 'Partitioning', 'u': 'Imbalanced'}
    labels2 = {'x': 'Dataset', 'y': 'No communication', 'z': 'Partitioning', 'u': 'Imbalanced'}
    if 'efficiency' in label:
        labels['y'] = 'Efficiency'
    if 'communication' in label:
        labels['y'] = 'Communication overhead'
    
    df = speedup_frame(data, task='%s stage1' % label, labels=labels)
    df2 = speedup_frame(data, task='%s stage2' % label, labels=labels2)
    df = order_frame(df, order=order)
    df2 = order_frame(df2, order=order)
    visualize.barplot_multi(df, df2, filename=img_file, labels=labels, x=labels['x'], 
        y=(labels['y'], labels2['y']), z=labels['z'])

def main():
    parser = argparse.ArgumentParser(version='0.1', description='crow-plot')
    parser.add_argument("-o", "--orthogonal", action="store_true", help='Select orthogonal NMTF')
    parser.add_argument("-a", "--action", default='speedup', help="Pick: benchmark, speedup, k, balance, efficiency, communication")
    
    parser.add_argument('args', nargs='*', help='Other args')
    args = parser.parse_args()
    
    argv = args.args
    if len(argv) == 0:
        raise Exception("No datasets selected")
    
    method = 'nmtf_long'
    if args.orthogonal:
        method = 'nmtf_ding'
    
    print 'Method', method
    image_folder = to_path(IMG, method)
    k = '20'
    max_iter = 100
    
    if args.action == 'benchmark':
        oargs = []
        if args.orthogonal:
            oargs = ['-o']
        p = subprocess.Popen(['python', 'benchmark.py'] + oargs + args, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
    
    elif args.action == 'speedup':
        all_data = read_wrapper(argv, method=method, task='speedup', max_iter=max_iter)
        img_file = to_path(image_folder, 'speedup_%s.png' % k)
        bar_plot(all_data, img_file, label='speedup', order=argv)
        
        all_data = read_wrapper(argv, method=method, task='best_speedup', context='gpu', max_iter=max_iter)
        img_file = to_path(image_folder, 'bspeedup.png')
        bar_plot(all_data, img_file, label='best', order=argv)
        
        all_data = read_wrapper(argv, method=method, task='best_speedup', context='cpu', max_iter=max_iter)
        img_file = to_path(image_folder, 'cspeedup.png')
        bar_plot(all_data, img_file, label='best cpu', order=argv)
    
    elif args.action == 'balance':
        for context in ['gpu', 'cpu']:
            all_data = read_wrapper(argv, method=method, task='balance', 
                context=context, max_iter=max_iter, k=k)
            print all_data
            img_file = to_path(image_folder, 'balanced_%s.png' % context)
            bar_plot(all_data, img_file, label='balance', k='20', order=argv)
        
    elif args.action == 'k':
        for context in ['gpu', 'cpu']:
            all_data = read_wrapper(argv, method=method, task='k', context=context, label='4', max_iter=max_iter)
            img_file = to_path(image_folder, 'rank_%s4.png' % context)
            line_plotter(all_data, img_file, label='%s4' % context, order=argv)
        
    elif args.action == 'efficiency':
        for context in ['gpu', 'cpu']:
            all_data = read_wrapper(argv, method=method, task='efficiency', context=context, max_iter=max_iter)
            img_file = to_path(image_folder, 'efficiency_%s.png' % context)
            bar_plot(all_data, img_file, label='efficiency %s' % context, order=argv)
        
    elif args.action == 'transfer':
        for context in ['gpu', 'cpu']:
            all_data = read_wrapper(argv, method=method, task='transfer', context=context, max_iter=max_iter)
            img_file = to_path(image_folder, 'transfer_%s.png' % context)
            multi_plot(all_data, img_file, label='transfer %s' % context, order=argv) 

    else:
        print "No action selected: use -a <action> argument"
    

if __name__ == '__main__':
    appdir = os.path.dirname(sys.argv[0])
    if appdir:
        os.chdir(appdir)
    print os.listdir(RESULTS)
    main()
