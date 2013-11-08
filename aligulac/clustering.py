#!/usr/bin/env python3

# {{{ Imports
import networkx
import networkx.readwrite.edgelist as edgelist
import networkx.algorithms.link_analysis as link_analysis
import networkx.algorithms.shortest_paths.generic as shortest_paths

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aligulac.settings')

from datetime import datetime
import subprocess
import sys

from django.db import connection, transaction

from ratings.models import (
    Period,
    Player,
    Cluster
)
# }}}

def log(msg):
    print('[%s] %s' % (str(datetime.now()), msg))

period = Period.objects.get(id=sys.argv[1])

log('Getting edge weights')

cur = connection.cursor()
pfrom, pto = period.id - 15, period.id # Inclusive
cur.execute('''
    SELECT
        id,
        pla_id,
        plb_id
    FROM match WHERE period_id >= %i AND period_id <= %i
''' % (pfrom, pto))
rows = cur.fetchall()

with open('/tmp/aligulac_30_per_matches.edgelist', 'w') as f:
    for id, pla_id, plb_id in rows:
        f.write('%i %i\n' % (pla_id, plb_id))

graph = edgelist.read_edgelist("/tmp/aligulac_30_per_matches.edgelist", "r")

log('Running page rank')

pr = link_analysis.pagerank(graph)

pr_list = [(k, pr[k]) for k in pr]
pr_list.sort(key=lambda x: -x[1])

log('Picking the 10 most connected players')

pids = [str(x[0]) for x in pr_list[:10]]

pid_inv = dict((pids[i], i) for i in range(len(pids)))

log('Measuring distance')

spaths = dict()
for pid in pids:
    spaths[pid] = shortest_paths.shortest_path_length(graph, target=pid)


def get_min(pid):
    m, i = None, -1
    for anchor in pids:
        if (m is None or spaths[anchor][pid] < m) and pid in spaths[anchor]:
            m, i = spaths[anchor][pid], pid_inv[anchor]

    return m, i

log('Minimizing')

cur.execute('''DELETE FROM cluster WHERE period_id = %i''' % period.id)

def create_cluster(pid):
    player = Player.objects.get(id=int(pid))

    x = Cluster()
    
    m, i = get_min(pid)
    x.period = period
    x.player = player
    x.cluster = i #  Set to -1 if no path exists
    x.distance = m # Set to null if no path exists

    return x

Cluster.objects.bulk_create(
    create_cluster(pid) for pid in graph.nodes()
)


# print('[%s] Markov clustering' % str(datetime.now()))

# with open(os.devnull, 'wb') as devnull:
#     subprocess.check_call([
#         '/home/efonn/local/mcl/bin/mcl', '/tmp/clusters.abc', '--abc', '-I', '2.3', '-o', '/tmp/clusters.out'
#     ], stdout=devnull, stderr=subprocess.STDOUT)

# clusters = []
# with open('/tmp/clusters.out') as f:
#     lines = f.readlines()
#     cluster = 1
#     for line in lines:
#         for player in line.split('\t'):
#             id = int(player.split('-')[0])
#             clusters.append((id, cluster))
#         cluster += 1

# print('[%s] Updating database (%i clusters)' % (str(datetime.now()), cluster-1))

# cur.execute('BEGIN')
# cur.execute('''
#     CREATE TEMPORARY TABLE temp_rating_clusters (
#         player_id integer PRIMARY KEY,
#         cluster integer
#     ) ON COMMIT DROP
# ''')
# cur.execute('INSERT INTO temp_rating_clusters VALUES ' + ', '.join(str(c) for c in clusters))
# cur.execute('''
#     UPDATE rating SET cluster=t.cluster
#     FROM temp_rating_clusters AS t WHERE rating.player_id=t.player_id AND rating.period_id=%i
# ''' % pid)
# cur.execute('COMMIT')
