#!/usr/bin/env bash
# !/usr/bin/env python

virtualenv abmenv
if [ -d "abenv/Scripts/" ]; then
    source abmenv/Scripts/activate
fi
if [ -d "abenv/bin/" ]; then
    source abmenv/bin/activate
fi

pip install -r requirements.txt