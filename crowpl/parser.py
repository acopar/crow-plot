import os
from utils import *


def cmp_configs(x, y):
    equal = True
    for key in y:
        if key not in x:
            continue
        if x[key] != str(y[key]):
            equal = False
    return equal

def read_datasets2(datasets, RESULTS='results'):
    all_data = {}
    
    for path in datasets:
        dataname = os.path.splitext(os.path.basename(path))[0]
        all_data[dataname] = []
        index_file = to_path(RESULTS, '%s.csv' % dataname)
        
        data = load_csv_dict(index_file)
        if not data:
            print 'Warning: File not found %s' % index_file
            continue
        
        for d in data:
            blocks = d['blocks']
            blocks = [int(b) for b in blocks.split('x')]
            h = float(d['time'])
            all_data[dataname].append(d)
            

    return all_data

def compare_configs(data, config):
    add = False
    for d in data:
        if cmp_configs(d, config):
            add = 'yes'
            return True
    return False