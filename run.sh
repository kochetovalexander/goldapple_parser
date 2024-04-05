#!/usr/bin/bash


date
until /usr/bin/python3 main.py
do
    echo ...
    date
    sleep 5
done
date
