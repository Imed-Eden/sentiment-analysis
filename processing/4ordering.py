# -*- coding: utf-8 -*-

import sys

metric = sys.argv[1]
with open("tmp", 'r') as file:
    toRank = file.read()
file.close()
toRank = eval(toRank)
ranked = str({k: v for k, v in sorted(toRank.items(), key=lambda item: item[1][metric])})
f = open("tmp_results", "w")
f.write(ranked)
f.close()

