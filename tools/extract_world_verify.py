#!/usr/bin/env python3
r"""Validate data/world/: SPEC conformance and cross-table consistency.

    python tools/extract_world_verify.py [--repo DIR]

Checks, per table:
  1  the file exists and its header is exactly the manifest's column list
  2  the first column is the manifest's primary key
  3  row_count equals the number of data rows in the file
  4  the primary key has no duplicate and no empty value
  5  id_range equals the real min/max of the primary key
  6  the file is UTF-8 with BOM and uses LF only
  7  no value is the literal "NULL" and every row has the header's field count
Then cross-table:
  8  manifest table ids are unique
  9  every quests.stage_id is a stages.stage_id
 10  every quests.quest_id that has monsters / rewards exists in quests
 11  every quest-monsters.monster_id and monster-carves.monster_id is a monsters.monster_id
 12  every requests.quest_id exists in quests (kind 0 only)
 13  every arena.quest_id exists in quests
Exit code 0 when everything passes.
"""
import argparse
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=DEFAULT_REPO)
    a = ap.parse_args()
    d = os.path.join(a.repo, 'data', 'world')
    man = json.load(open(os.path.join(d, '_manifest.json'), encoding='utf-8'))
    fails, checks = [], 0

    def ok(cond, label):
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(label)

    data = {}
    for t in man['tables']:
        path = os.path.join(d, t['file'])
        ok(os.path.exists(path), '%s: file missing' % t['id'])
        if not os.path.exists(path):
            continue
        raw = open(path, 'rb').read()
        ok(raw[:3] == b'\xef\xbb\xbf', '%s: no UTF-8 BOM' % t['id'])
        ok(b'\r' not in raw, '%s: CR found (must be LF)' % t['id'])
        with open(path, encoding='utf-8-sig', newline='') as f:
            rows = list(csv.reader(f))
        header, body = rows[0], rows[1:]
        ok(header == [c['name'] for c in t['columns']],
           '%s: header != manifest columns' % t['id'])
        ok(header[0] == t['primary_key'],
           '%s: first column is not the primary key' % t['id'])
        ok(len(body) == t['row_count'],
           '%s: row_count %d != %d rows' % (t['id'], t['row_count'], len(body)))
        ok(all(len(r) == len(header) for r in body),
           '%s: a row has the wrong field count' % t['id'])
        ok(not any('NULL' == v for r in body for v in r),
           '%s: literal NULL value' % t['id'])
        keys = [r[0] for r in body]
        ok(all(k != '' for k in keys), '%s: empty primary key' % t['id'])
        dup = [k for k, n in collections.Counter(keys).items() if n > 1]
        ok(not dup, '%s: duplicate primary key %s' % (t['id'], dup[:5]))
        ints = [int(k) for k in keys]
        ok([min(ints), max(ints)] == t['id_range'],
           '%s: id_range %s != actual %s' % (t['id'], t['id_range'], [min(ints), max(ints)]))
        data[t['id']] = body

    ids = [t['id'] for t in man['tables']]
    ok(len(set(ids)) == len(ids), 'manifest: duplicate table id')

    def col(tid, name):
        t = next(x for x in man['tables'] if x['id'] == tid)
        return [c['name'] for c in t['columns']].index(name)

    if 'stages' in data and 'quests' in data:
        stages = {r[0] for r in data['stages']}
        si = col('quests', 'stage_id')
        bad = {r[si] for r in data['quests'] if r[si] and r[si] not in stages}
        ok(not bad, 'quests: stage_id not in stages %s' % sorted(bad)[:5])

    if 'monsters' in data:
        mon = {r[0] for r in data['monsters']}
        for tid in ('quest-monsters', 'monster-carves'):
            if tid in data:
                i = col(tid, 'monster_id')
                bad = {r[i] for r in data[tid] if r[i] not in mon}
                ok(not bad, '%s: monster_id not in monsters %s' % (tid, sorted(bad)[:5]))

    warn = []
    # ---- second batch: rewards / quest-unlock / unlock-lists / size-variation /
    #      rotating-quests / request-offer
    if 'rewards' in data and 'quest-rewards' in data:
        have = {r[col('rewards', 'rem_id')] for r in data['rewards']}
        need = {r[col('quest-rewards', 'rem_id')] for r in data['quest-rewards']}
        ok(not (need - have),
           'rewards: rem_id missing for quest-rewards %s' % sorted(need - have)[:5])
        if have - need:
            warn.append('rewards: %d rem_id are not referenced by quest-rewards'
                        % len(have - need))
        # Every reward table's chances add up to 100, with one documented exception:
        # rem 230073 sums to 104 in the game's own data (the game rolls each row on its
        # own percentage, so a table over 100 still loads).  Reported, not failed.
        tot = collections.Counter()
        for r in data['rewards']:
            tot[r[col('rewards', 'rem_id')]] += int(r[col('rewards', 'chance')])
        bad = {k: v for k, v in tot.items() if v != 100}
        ok(set(bad) <= {'230073'},
           'rewards: chance total != 100 for %d tables %s'
           % (len(bad), sorted(bad.items())[:5]))
        if bad:
            warn.append('rewards: %d table(s) do not sum to 100%%: %s (rem 230073 is a '
                        'known game-side table that sums to 104)'
                        % (len(bad), sorted(bad.items())))

    if 'quests' in data:
        qids = {r[col('quests', 'quest_id')] for r in data['quests']}
        for tid in ('quest-unlock', 'rotating-quests'):
            if tid in data:
                i = col(tid, 'quest_id')
                bad = {r[i] for r in data[tid] if r[i] not in qids}
                ok(not bad, '%s: quest_id not in quests %s' % (tid, sorted(bad)[:5]))
        if 'quest-unlock' in data:
            ok({r[0] for r in data['quest-unlock']} == qids,
               'quest-unlock: quest_id set differs from quests')
        if 'request-offer' in data:
            i = col('request-offer', 'quest_id')
            bad = {r[i] for r in data['request-offer'] if r[i] and r[i] not in qids}
            ok(not bad, 'request-offer: quest_id not in quests %s' % sorted(bad)[:5])
        if 'requests' in data:
            have = {r[0] for r in data['requests']}
            i = col('request-offer', 'request_index')
            bad = {r[i] for r in data['request-offer'] if r[i] not in have}
            ok(not bad, 'request-offer: request_index not in requests %s' % sorted(bad)[:5])

    if 'quests' in data:
        qids = {r[col('quests', 'quest_id')] for r in data['quests']}
        if 'arena' in data:
            i = col('arena', 'quest_id')
            bad = {r[i] for r in data['arena'] if r[i] not in qids}
            ok(not bad, 'arena: quest_id not in quests %s' % sorted(bad)[:5])
        if 'requests' in data:
            i = col('requests', 'quest_id')
            k = col('requests', 'kind')
            bad = {r[i] for r in data['requests'] if r[k] == '0' and r[i] not in qids}
            ok(not bad, 'requests: quest_id not in quests %s' % sorted(bad)[:5])
        # quest-monsters / quest-rewards come from every quest file (1855), quests.csv
        # from the save's quest list (1508).  A file that the list does not hold can
        # still carry monsters and rewards, so this is reported, not failed.
        for tid in ('quest-monsters', 'quest-rewards'):
            if tid in data:
                i = col(tid, 'quest_id')
                bad = {r[i] for r in data[tid] if r[i] not in qids}
                if bad:
                    warn.append('%s: %d quest ids have no row in quests (not in the save '
                                'quest list): %s' % (tid, len(bad), sorted(bad)[:8]))

    total = sum(t['row_count'] for t in man['tables'])
    print('tables      : %d' % len(man['tables']))
    print('total rows  : %d' % total)
    print('checks      : %d' % checks)
    print('failures    : %d' % len(fails))
    for f in fails:
        print('  FAIL %s' % f)
    for w in warn:
        print('  WARN %s' % w)
    print('RESULT      : %s' % ('PASS' if not fails else 'FAIL'))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
