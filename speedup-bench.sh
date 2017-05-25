#!/bin/bash

python crowpl/benchmark.py ArrayExpress TCGA-BRCA fetus retina cochlea
scripts/crow-plot python /app/crowpl -a speedup ArrayExpress TCGA-BRCA fetus retina cochlea
