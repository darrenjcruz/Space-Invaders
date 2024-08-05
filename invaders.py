#!/usr/bin/env python3
# Darren Cruz
# CPSC 386-02
# 2023-04-19
# darrencruz@csu.fullerton.edu
# @darrenjcruz
#
# Lab 05-00
#
# This is the hello module, it imports the game and runs it.
#


"""
Imports the the game demo and executes the main function.
"""


import sys
import game


def main():
    """main function."""
    videogame = game.MyVideoGame()
    videogame.run()


if __name__ == "__main__":
    main()
    sys.exit(0)
