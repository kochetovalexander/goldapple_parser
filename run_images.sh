#!/usr/bin/bash


date
until /usr/bin/python3 extract_images.py
do
    echo NEXT ATTEMPT
    date
    sleep 5
done
date
