#!/bin/bash

python crowpl/benchmark.py $1 -i -u fetus retina cochlea
scripts/crow-plot python /app/crowpl -a balance fetus retina cochlea
