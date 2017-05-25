#!/usr/bin/env python

import os
import cPickle
import time
import csv

def ensure_dir(f):
    d = os.path.dirname(f)
    if d:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
            except OSError, e:
                print f
                raise e

def ensure_dir_exact(d):
    d = os.path.join(d, '')
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError, e:
            print d
            raise e

def load_file(filename):
    # load pickle file
    if os.path.isfile(filename) == False:
        print "Error: Cannot open file: %s" % filename
        return None
    fp = open(filename, 'rb')
    d = cPickle.load(fp)
    fp.close()
    return d

def dump_file(filename, data):
    # dump pickle file
    ensure_dir(filename)
    fp = open(filename, 'wb')
    cPickle.dump(data, fp, 2)
    fp.close()

def file_concat(parts):
    path = ''
    for i in range(len(parts)):
        path = os.path.join(path, parts[i])
    return path

def to_path(*parts):
    return file_concat(parts)

def check_file(f, soft=False):
    if not os.path.isfile(f):
        if soft == True:
            return False
        else:
            raise Exception("File not found %s" % f)
    return True

### Filebase ###

def get_filebase(path):
    basename = os.path.basename(path)
    filebase, ext = os.path.splitext(basename)
    return filebase

def glob_filebase(exp):
    files = glob.glob(exp)
    return [get_filebase(f) for f in files]

def list_filebase(path):
    files = os.listdir(path)
    return [get_filebase(f) for f in files]

def filter_filebase(files):
    return [get_filebase(f) for f in files]

### Extensions ###

def get_extension(path):
    basename = os.path.basename(path)
    filebase, ext = os.path.splitext(basename)
    return ext

def filter_extensions(files, valid_ext):
    return [f for f in files if get_extension(f) in valid_ext]

def load_csv_dict(filename, delimiter=','):
    # loads csv file into array of rows (arrays)
    ensure_dir(filename)
    if not os.path.isfile(filename):
        print "Error: Cannot open file: %s" % filename
        return None
    
    fp = open(filename)
    
    reader = csv.reader(fp, delimiter=delimiter)
    try:
        attributes = reader.next()
    except StopIteration:
        fp.close()
        return None
    data = []
    try:
        for row in reader:
            data.append({a:row[i] for i,a in enumerate(attributes)})
    except Exception, e:
        print traceback.format_exc()
        print "Filename", filename
        return None
    fp.close()
    return data

def save_csv_dict(filename, data, columns=None, append=False):
    # write csv file (dict)
    ensure_dir(filename)
    new_file = False
    if not os.path.isfile(filename):
        new_file = True
    
    if append:
        fp = open(filename, 'a')
    else:
        fp = open(filename, 'w')
    if not fp:
        print "Error: Cannot open file: %s" % filename
        return None
    
    writer = csv.writer(fp, delimiter=',')
    attributes = None
    if columns != None:
        attributes = columns
    else:
        if len(data) == 0:
            print "Error: write_csv_dict: no data to write"
            return None
        attributes = sorted(data[0].keys())
    if append == False or new_file:
        writer.writerow([a for a in attributes])
    
    for line in data:
        writer.writerow([line[a] if a in line else '' for a in attributes])
    fp.close()