"""Load test for the distributed banking system.

Generates a larger transaction file, runs bin/banking with 3 clusters x 3 servers,
and prints the numbers to put on the resume. Your original CSV is restored afterwards.
Run from the repo folder:  python3 load_test.py
"""
import os, random, re, shutil, subprocess, glob

import sys
KEEP = "--keep" in sys.argv          # --keep saves a copy of the databases in diag_dbs/ for debugging
args = [a for a in sys.argv[1:] if a != "--keep"]
SETS, PER_SET, SEED = (int(args[0]) if args else 50), 20, 7
CSV = "New_Test_Cases_-_Lab3.csv"
SERVERS = [f"S{i}" for i in range(1, 10)]
CONTACTS = ["S1", "S4", "S7"]

def cluster(acct):          # accounts 1-1000 -> C1, 1001-2000 -> C2, 2001-3000 -> C3
    return (acct - 1) // 1000

random.seed(SEED)
rows, cross, failure_sets = [], 0, 0
for s in range(1, SETS + 1):
    active = SERVERS[:]
    if s % 5 == 4:                      # sets 4, 9, 14, ...: one non-contact server per cluster is down
        failure_sets += 1
        for down in ("S3", "S6", "S9"):
            active.remove(down)
    for t in range(PER_SET):
        a, b = random.sample(range(1, 3001), 2)
        cross += cluster(a) != cluster(b)
        txn = f"({a}, {b}, 1)"
        if t == 0:
            rows.append(f'{s},"{txn}","[{", ".join(active)}]","[{", ".join(CONTACTS)}]"')
        else:
            rows.append(f',"{txn}",,')

shutil.copy(CSV, CSV + ".bak")
backup_dir = "db_backup_before_load_test"
os.makedirs(backup_dir, exist_ok=True)
for db in glob.glob("db_S*.db"):
    shutil.move(db, os.path.join(backup_dir, db))
try:
    open(CSV, "w").write("\n".join(rows) + "\n")
    feed = "3\n3\n" + "1\n" * (SETS - 1) + "4\n1\n" + "1\n" * 20   # extra lines so the menu never runs out of input
    with open("load_test_output.log", "w") as f:
        subprocess.run(["./bin/banking"], input=feed, stdout=f, stderr=subprocess.STDOUT, text=True, timeout=1800)
    out = open("load_test_output.log").read()
    import sqlite3
    state = {}
    for i in range(1, 10):
        con = sqlite3.connect(f"db_S{i}.db")
        state[i] = dict(con.execute("SELECT client_id, balance FROM clients").fetchall())
        con.close()
    if KEEP:
        os.makedirs("diag_dbs", exist_ok=True)
        for i in range(1, 10):
            shutil.copy(f"db_S{i}.db", os.path.join("diag_dbs", f"db_S{i}.db"))
    replicas_match = all(state[c*3+1] == state[c*3+2] == state[c*3+3] for c in range(3))
    total_money = sum(sum(state[c*3+1].values()) for c in range(3))
finally:
    shutil.move(CSV + ".bak", CSV)
    for db in glob.glob("db_S*.db"):
        os.remove(db)
    for db in glob.glob(os.path.join(backup_dir, "*.db")):
        shutil.move(db, os.path.basename(db))
    os.rmdir(backup_dir)

total = SETS * PER_SET
committed = re.findall(r"Total Transactions: (\d+)", out)
latency = re.findall(r"Average Latency per Transaction: (\S+)", out)
tput = re.findall(r"Throughput: ([\d.]+)", out)
print(f"Submitted transactions : {total}")
print(f"Cross-shard (2PC)      : {cross} ({100*cross/total:.0f}%)")
print(f"Sets with servers down : {failure_sets} of {SETS} (3 of 9 servers down)")
print(f"Committed              : {committed[-1] if committed else '?'}")
print(f"Average latency        : {latency[-1] if latency else '?'}")
print(f"Throughput             : {tput[-1] if tput else '?'} transactions/s")
print(f"Replicas identical     : {'yes' if replicas_match else 'NO'} (all 3 servers in each cluster)")
print(f"Total money conserved  : {'yes' if total_money == 30000 else 'NO'} ({total_money} of 30000)")
print("Full log: load_test_output.log")
