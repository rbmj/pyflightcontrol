#!/bin/bash

. services

launch () {
    ( $1 & ) 0<&- 2> error.log > out.log &
}

for s in $SERVICES
do
    launch $(dirname $0)/$s
done
