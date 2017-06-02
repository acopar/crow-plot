import subprocess
import pandas as pd
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
import seaborn as sns
from seaborn.palettes import *
    
from utils import *


def order_hue(df, z='Blocks'):
    hue_set = set([])
    for i in df.index:
        b = df.ix[i][z]
        hue_set.add(b)
    horder = sorted(list(hue_set))
    horder = [str(x) for x in horder]
    return horder

def skip_block1(df):
    df = df[df['Blocks'] != '1 x 1']
    return df

def get_palette(n_colors, start=0, variant="deep"):
    colors = sns.color_palette(variant, n_colors)
    if start != 0:
        colors = colors[start:]
    return colors

def standard_plot(f):
    def new_f(*args, **kwargs):
        sns.set_context("paper")
        #sns.plotting_context(font_scale=10)
        sns.set(style="whitegrid", font_scale=2.0)
        matplotlib.rcParams['text.usetex'] = True
        #matplotlib.rcParams['axes.labelsize'] = 12
        #matplotlib.rcParams['axes.titlesize'] = 12
        #matplotlib.rcParams['ytick.labelsize'] = 11
        #matplotlib.rcParams['xtick.labelsize'] = 11
        
        bbox = f(*args, **kwargs)
        filename = kwargs['filename']
        if 'labels' in kwargs:
            labels = kwargs['labels']
            #if 'title' in labels:
            #    plt.title(labels['title'])
            if 'xlabel' in labels:
                plt.xlabel(labels['xlabel'])
            if 'ylabel' in labels:
                plt.ylabel(labels['ylabel'])
        
        if filename:
            ensure_dir(filename)
            pdf = filename.replace('.png', '.pdf')
            if bbox == 'one':
                plt.gcf().tight_layout(rect=[0,0,0.85,1])
                plt.savefig(pdf)
            else:
                plt.savefig(pdf, bbox_inches="tight", pad_inches=0.2)
            # Comment to disable conversion from pdf to png
            p = subprocess.Popen(['convert', pdf, filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
        plt.close()
    return new_f

@standard_plot
def factorplot(df, filename=None, labels=None, y=None, z='Blocks'):
    if y == None:
        print "Error: Factorplot: Please select column."
        print "Columns:", df.columns
        raise Exception()
    
    g = sns.factorplot(x='label', y=y, hue=z, data=df, size=8, kind="bar")
    g.despine(left=True)

@standard_plot
def barplot(df, filename=None, labels=None, x='label', y=None, z='Blocks', start=0):
    if y == None:
        print "Error: Factorplot: Please select column."
        print "Columns:", df.columns
        raise Exception()
    
    f, ax = plt.subplots(figsize=(13, 9))
    horder = order_hue(df, z=z)
    palette = get_palette(len(horder), start=start)
    sns.barplot(x=x, y=y, hue=z, data=df, palette=palette)
    ax.set(ylabel=y)
    ax.legend(title=z, loc="center left", bbox_to_anchor=(1, 0.5))
    sns.despine(left=True)

@standard_plot
def barplot_multi(df, df2, filename=None, labels=None, x='label', y=None, z='Blocks', start=0):
    if y == None or len(y) < 2:
        print "Error: Factorplot: Please select column."
        print "Columns:", df.columns
        raise Exception()
    
    f, ax = plt.subplots(figsize=(13, 9))
    horder = order_hue(df, z=z)
    palette = get_palette(len(horder), start=start, variant="deep")
    palette2 = []
    for i, p in enumerate(palette):
        q = (min(p[0]+0.25, 1), min(p[1]+0.25, 1), min(p[2]+0.25, 1))
        palette2.append(q)
    palette3 = get_palette(len(horder), start=start, variant="dark")
    
    sns.barplot(x=x, y=y[1], hue=z, data=df2, palette=palette2)
    sns.barplot(x=x, y=y[0], hue=z, data=df, palette=palette)
    handles, labels = ax.get_legend_handles_labels()

    hnd = handles[6:12]
    lab = labels[6:12]
    l2 = ax.legend(hnd, lab, title="Efficiency", loc="center left", bbox_to_anchor=(1.022, 0.3))
    l2.get_title().set_fontsize('16')
    plt.gca().add_artist(l2)
    
    hnd = handles[:6]
    lab = labels[:6]
    l1 = ax.legend(hnd, lab, title="Communication\noverhead", loc="center left", bbox_to_anchor=(1.009, 0.7))
    l1.get_title().set_fontsize('16')
    plt.gca().add_artist(l1)
    
    l2.set_visible(False)
    
    hnd = handles[6:12]
    lab = labels[6:12]
    l2 = ax.legend(hnd, lab, title="Efficiency", loc="center left", bbox_to_anchor=(1.022, 0.3))
    l2.get_title().set_fontsize('16')
    plt.gca().add_artist(l2)
    
    ax.set(ylabel="Efficiency")
    sns.despine(left=True)
    return "one"

@standard_plot
def lineplot(df, filename=None, labels=None, x='Dataset', y=None, z='Blocks'):
    if y == None:
        print "Error: Factorplot: Please select column."
        print "Columns:", df.columns
        raise Exception()
    
    matplotlib.rcParams['lines.linewidth'] = 1.5
    g = sns.factorplot(x=x, y=y, hue=z, data=df, size=8, legend=False, aspect=1.44)
    g.set(ylim=(0, None))
    labels = [i if i%20 == 0 else '' for i in range(10,150,10)]
    g.set(xticklabels=labels)

    g.add_legend(title="Dataset", bbox_to_anchor=(1.2, 0.5), 
        label_order=["Retina", "Cochlea", "Fetus", "E-TABM-185", "TCGA-BRCA"])
    g.despine(left=True)
    
@standard_plot
def standard_lineplot(df, filename=None, labels=None, x='Dataset', y=None, z='Blocks', skipxlabels=10, xlabelrange=100):
    if y == None:
        print "Error: Factorplot: Please select column."
        print "Columns:", df.columns
        raise Exception()
    
    matplotlib.rcParams['lines.linewidth'] = 1.0
    f, ax = plt.subplots(figsize=(13, 9))
    sns.factorplot(x=x, y=y, hue=z, data=df)
                   #capsize=0.01, size=7, aspect=1.0) # palette="YlGnBu_d"
    labels = [i if int(i)%skipxlabels == 0 else '' for i in range(0,xlabelrange)]
    sns.set(xticklabels=labels)

    sns.despine(left=True)