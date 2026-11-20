"""Shows that a secret passed on a command line is visible in the process list.

Mimics step 2 of the skill: curl -s -H "Authorization: Bearer $RELAY_KEY" ...
We use a harmless stand-in process and a FAKE key, then look for it with `ps`,
the same way any other user on the machine could.

Run:  python3 demo_ps_leak.py
"""
import subprocess
import sys
import time

FAKE_KEY = "rly_Ab3dE6gH9jK2mN5pQ8sT1vX4"  # fake
HEADER = f"Authorization: Bearer {FAKE_KEY}"

# Stand-in for curl: sleeps 5 seconds, with the header as a command-line argument.
victim = subprocess.Popen(
    [sys.executable, "-c", "import time; time.sleep(5)", "-H", HEADER]
)
time.sleep(1)

# What another user on the machine could run (-A = all users' processes).
ps = subprocess.run(
    ["ps", "-A", "-o", "pid,user,args"], capture_output=True, text=True
).stdout

print("Command run by the 'victim' process: <python> -c ... -H", repr(HEADER))
print()
print("Lines in `ps -A -o pid,user,args` that contain the fake key:")
found = False
for line in ps.splitlines():
    if FAKE_KEY in line:
        found = True
        print("  ", line)
print()
print("SECRET VISIBLE IN PROCESS LIST:", found)

victim.kill()
