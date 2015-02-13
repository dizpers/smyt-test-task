#!/bin/sh
( cd spool/pids &&
for pidfile in *.pid; do kill -QUIT `cat $pidfile`; done
)