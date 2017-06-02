#!/bin/bash

python crowpl/benchmark.py -c -u ArrayExpress TCGA-BRCA fetus retina cochlea
scripts/crow-plot python /app/crowpl -a efficiency ArrayExpress TCGA-BRCA fetus retina cochlea
scripts/crow-plot python /app/crowpl -a one ArrayExpress TCGA-BRCA fetus retina cochlea
