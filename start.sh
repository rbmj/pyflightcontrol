#!/bin/bash

. services

launch () {
    dir=`dirname $0`
    ( $dir/$1.py & ) 0<&- 2> $dir/$1.error.log > $dir/$1.out.log &
}

for s in $SERVICES
do
    launch $s
done
