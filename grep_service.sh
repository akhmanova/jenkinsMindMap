#!/usr/bin/env bash

for service in $(cat ./services)
do
    STRING=""
    for file in $(ls ./output/ | cat)
    do
        RESULT=$(grep -C 3 "$service" ./output)
        echo $RESULT
    done
#awk -F"," 'BEGIN { OFS = "," } {$4="THERE"; print}' result.csv > output.csv
done