#!/bin/bash

python crowpl/benchmark.py $1 -u ArrayExpress TCGA-BRCA fetus retina cochlea
scripts/crow-plot python /app/crowpl -a speedup ArrayExpress TCGA-BRCA fetus retina cochlea
