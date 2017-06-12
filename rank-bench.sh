#!/bin/bash

python crowpl/benchmark.py $1 -r -u ArrayExpress TCGA-BRCA fetus retina cochlea
scripts/crow-plot python /app/crowpl -a k ArrayExpress TCGA-BRCA fetus retina cochlea
