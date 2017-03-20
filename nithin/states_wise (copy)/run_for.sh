#!/usr/bin/env bash

function map {
    if [ ! -d "$1/mapped" ]; then
        mkdir "$1/mapped"
    fi
    if [ ! -f "$1/village_list.csv" ] || [ ! -d "$1/input" ] || [ ! -d "$1/lgd" ] ; then
        echo "essential files not found, please check ..."
        exit
    fi
    echo "number of districts in input :" $(ls "$1/input" | wc -l)
    echo "number of districts in input :" $(ls "$1/lgd" | wc -l)
    echo "begin mapping ..."
#    ./village_mapper.py "$1"
}

if [ -d "$1" ] ; then
    echo "Running for " "$1"
    if [ -f  "$1/main.csv" ]; then
        echo "main.csv exists, doing name conversion"
        ./name_to_id.py "$1"
    fi
    map "$1"
fi

