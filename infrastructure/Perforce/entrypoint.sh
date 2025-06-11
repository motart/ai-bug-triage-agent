#!/bin/bash
set -e

# Initialize Perforce server on first run
if [ ! -f "$P4ROOT/db.have" ]; then
    p4d -r "$P4ROOT" -p "$P4PORT" -d
    sleep 3
    if ! /usr/bin/p4 -p localhost:$P4PORT users | grep -q "^$P4USER "; then
        /usr/bin/p4 -p localhost:$P4PORT user -f -i <<P4EOF
User: $P4USER
Type: super
Email: admin@example.com
FullName: Administrator
P4EOF
        echo -e "$P4PASSWD\n$P4PASSWD" | /usr/bin/p4 -p localhost:$P4PORT passwd $P4USER
    fi
    /usr/bin/p4 -p localhost:$P4PORT admin stop
fi

exec p4d -r "$P4ROOT" -p "$P4PORT" -d --foreground
