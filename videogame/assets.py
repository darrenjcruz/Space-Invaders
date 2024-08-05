#!/usr/bin/env python3
# Darren Cruz
# CPSC 386-02
# 2023-04-19
# darrencruz@csu.fullerton.edu
# @darrenjcruz
#
# Lab 05-00
#
# This is the assets module that contains the assets.
#


"""Assets to create PyGame based games."""


import os

main_dir = os.path.dirname(__file__)
data_dir = os.path.join(main_dir, "data")

asset_dict = {
    "explosion": "explosion.gif",
    "explosion2": "explosion2.gif",
    "explosionsfx": "Pillsbury.aif",
    "player": "BlueRedGreen_Spacecraft_V1.0.png",
    "bullets": "laser-bolts.png",
    "bullet": "laser-bolt.png",
    "soundtrack": "spaceship_shooter.mp3",
    "soundtrack2": "8bp051-06-random-happy_ending_after_all.mp3",
}


def get(key):
    """gets the path of the asset from the asset_dict"""
    key_path = asset_dict.get(key, None)
    if key_path:
        key_path = os.path.join(data_dir, key_path)
    return key_path
