#!/bin/bash

python crowpl/benchmark.py $1 -c -u ArrayExpress TCGA-BRCA fetus retina cochlea
scripts/crow-plot python /app/crowpl -a efficiency ArrayExpress TCGA-BRCA fetus retina cochlea
scripts/crow-plot python /app/crowpl -a transfer ArrayExpress TCGA-BRCA fetus retina cochlea
