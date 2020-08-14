#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
#                                                       ____      _     _      
#                                                      | __ ) ___(_) __| | ___ 
#                                                      |  _ \/ __| |/ _` |/ _ \
#                                                      | |_) \__ \ | (_| |  __/
#                                                      |____/|___/_|\__,_|\___|
#               
#============================================================(C) JPL 2020=======

import os
import random
import pkg_resources

import utils

#-------------------------------------------------------------------------------
# Class scratchAdjective
#-------------------------------------------------------------------------------
class scratchAdjective:
    
    def __init__(self, adjective):
        self.adjective = adjective
          
scratchAdjectives = []

scratchAdjectives.append(scratchAdjective("tiny"))
scratchAdjectives.append(scratchAdjective("big"))
scratchAdjectives.append(scratchAdjective("shiny"))
scratchAdjectives.append(scratchAdjective("fast"))
scratchAdjectives.append(scratchAdjective("furious"))
scratchAdjectives.append(scratchAdjective("slow"))
scratchAdjectives.append(scratchAdjective("gentle"))
scratchAdjectives.append(scratchAdjective("slim"))
scratchAdjectives.append(scratchAdjective("tall"))
scratchAdjectives.append(scratchAdjective("thin"))
scratchAdjectives.append(scratchAdjective("short"))
scratchAdjectives.append(scratchAdjective("sharp"))
scratchAdjectives.append(scratchAdjective("happy"))
scratchAdjectives.append(scratchAdjective("bored"))
scratchAdjectives.append(scratchAdjective("lucky"))
scratchAdjectives.append(scratchAdjective("strong"))
scratchAdjectives.append(scratchAdjective("weak"))
scratchAdjectives.append(scratchAdjective("mad"))
scratchAdjectives.append(scratchAdjective("tired"))
scratchAdjectives.append(scratchAdjective("clever"))
scratchAdjectives.append(scratchAdjective("smart"))
scratchAdjectives.append(scratchAdjective("light"))
scratchAdjectives.append(scratchAdjective("heavy"))
scratchAdjectives.append(scratchAdjective("foolish"))
scratchAdjectives.append(scratchAdjective("black"))
scratchAdjectives.append(scratchAdjective("white"))
scratchAdjectives.append(scratchAdjective("blue"))
scratchAdjectives.append(scratchAdjective("green"))
scratchAdjectives.append(scratchAdjective("red"))
scratchAdjectives.append(scratchAdjective("yellow"))
scratchAdjectives.append(scratchAdjective("brown"))
scratchAdjectives.append(scratchAdjective("pink"))
scratchAdjectives.append(scratchAdjective("purple"))
scratchAdjectives.append(scratchAdjective("orange"))
scratchAdjectives.append(scratchAdjective("silver"))
scratchAdjectives.append(scratchAdjective("gold"))
scratchAdjectives.append(scratchAdjective("noisy"))
scratchAdjectives.append(scratchAdjective("freaky"))
scratchAdjectives.append(scratchAdjective("little"))
scratchAdjectives.append(scratchAdjective("hairy"))
scratchAdjectives.append(scratchAdjective("bold"))
scratchAdjectives.append(scratchAdjective("brave"))
scratchAdjectives.append(scratchAdjective("fat"))
scratchAdjectives.append(scratchAdjective("rude"))
scratchAdjectives.append(scratchAdjective("pretty"))

#-------------------------------------------------------------------------------
# Class scratchAnimal
#-------------------------------------------------------------------------------
class scratchAnimal:
    
    def __init__(self, animal):
        self.animal = animal
          
scratchAnimals = []

scratchAnimals.append(scratchAnimal("dog"))
scratchAnimals.append(scratchAnimal("cat"))
scratchAnimals.append(scratchAnimal("bee"))
scratchAnimals.append(scratchAnimal("wasp"))
scratchAnimals.append(scratchAnimal("hornet"))
scratchAnimals.append(scratchAnimal("fish"))
scratchAnimals.append(scratchAnimal("cow"))
scratchAnimals.append(scratchAnimal("puppy"))
scratchAnimals.append(scratchAnimal("bird"))
scratchAnimals.append(scratchAnimal("parrot"))
scratchAnimals.append(scratchAnimal("canary"))
scratchAnimals.append(scratchAnimal("turtle"))
scratchAnimals.append(scratchAnimal("rabbit"))
scratchAnimals.append(scratchAnimal("mouse"))
scratchAnimals.append(scratchAnimal("snake"))
scratchAnimals.append(scratchAnimal("lizard"))
scratchAnimals.append(scratchAnimal("pony"))
scratchAnimals.append(scratchAnimal("horse"))
scratchAnimals.append(scratchAnimal("pig"))
scratchAnimals.append(scratchAnimal("hen"))
scratchAnimals.append(scratchAnimal("rooster"))
scratchAnimals.append(scratchAnimal("goose"))
scratchAnimals.append(scratchAnimal("turkey"))
scratchAnimals.append(scratchAnimal("duck"))
scratchAnimals.append(scratchAnimal("sheep"))
scratchAnimals.append(scratchAnimal("ram"))
scratchAnimals.append(scratchAnimal("lamb"))
scratchAnimals.append(scratchAnimal("goat"))
scratchAnimals.append(scratchAnimal("donkey"))
scratchAnimals.append(scratchAnimal("bull"))
scratchAnimals.append(scratchAnimal("ox"))
scratchAnimals.append(scratchAnimal("calf"))
scratchAnimals.append(scratchAnimal("hare"))
scratchAnimals.append(scratchAnimal("beetle"))
scratchAnimals.append(scratchAnimal("snail"))
scratchAnimals.append(scratchAnimal("slug"))
scratchAnimals.append(scratchAnimal("ant"))
scratchAnimals.append(scratchAnimal("spider"))
scratchAnimals.append(scratchAnimal("worm"))
scratchAnimals.append(scratchAnimal("dove"))
scratchAnimals.append(scratchAnimal("crow"))
scratchAnimals.append(scratchAnimal("swan"))
scratchAnimals.append(scratchAnimal("fox"))
scratchAnimals.append(scratchAnimal("owl"))
scratchAnimals.append(scratchAnimal("beaver"))
scratchAnimals.append(scratchAnimal("bat"))
scratchAnimals.append(scratchAnimal("weasel"))
scratchAnimals.append(scratchAnimal("deer"))
scratchAnimals.append(scratchAnimal("doe"))
scratchAnimals.append(scratchAnimal("tuna"))
scratchAnimals.append(scratchAnimal("salmon"))
scratchAnimals.append(scratchAnimal("lobster"))
scratchAnimals.append(scratchAnimal("shrimp"))
scratchAnimals.append(scratchAnimal("whale"))
scratchAnimals.append(scratchAnimal("shark"))
scratchAnimals.append(scratchAnimal("dolphin"))
scratchAnimals.append(scratchAnimal("walrus"))
scratchAnimals.append(scratchAnimal("seal"))
scratchAnimals.append(scratchAnimal("otter"))
scratchAnimals.append(scratchAnimal("panda"))
scratchAnimals.append(scratchAnimal("tiger"))
scratchAnimals.append(scratchAnimal("lion"))
scratchAnimals.append(scratchAnimal("bear"))
scratchAnimals.append(scratchAnimal("frog"))
scratchAnimals.append(scratchAnimal("toad"))

#-------------------------------------------------------------------------------
# getRandomName()
#-------------------------------------------------------------------------------
def getRandomName(extension = "py"):
    random.seed()
    return ("%s_%s_%03d%s%s" % (random.choice(scratchAdjectives).adjective, random.choice(scratchAnimals).animal, random.randint(0, 999), "." if extension != "" else "", extension))

#-------------------------------------------------------------------------------
# createScratchFile()
#-------------------------------------------------------------------------------
def createScratchFile(folder):    
    while True:
        name = getRandomName()
        if utils.createFile(folder, name):
            break
    filename = os.path.join(folder, name)
    with open(pkg_resources.resource_filename(__name__, "resources/templates/newfiles/python/Python/main.py")) as f1:
        with open(filename, "w") as f2:
            for line in f1:
                f2.write(line) 
    return (filename)
    