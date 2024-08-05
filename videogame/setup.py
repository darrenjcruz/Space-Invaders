#!/usr/bin/env python3
# Darren Cruz
# CPSC 386-02
# 2023-04-19
# darrencruz@csu.fullerton.edu
# @darrenjcruz
#
# Lab 05-00
#
# This is the setup module for invaders, it contains the setup information.
#


""" Simple setup.py """


from setuptools import setup


setup_info = {
    "name": "videogame",
    "version": "0.1",
    "description": "A package to support writing games with PyGame",
    "long_description": open("../README.md").read(),
    "author": "Darren Cruz",
    "author_email": "darrencruz@csu.fullerton.edu",
    "url": "https://github.com/cpsc-spring-2023/cpsc-386-05-invaders-darrenjcruz",
}

setup(**setup_info)
