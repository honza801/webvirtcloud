#!/usr/bin/python

import hotshot.stats
import sys

stats = hotshot.stats.load(sys.argv[1])
#stats.strip_dirs()
#stats.sort_stats('time', 'calls')
stats.sort_stats('calls', 'time')

if len(sys.argv) > 2:
    stats.print_stats(int(sys.argv[2]))
else:
    stats.print_stats()
