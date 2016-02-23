from enum import Enum

class IonType(Enum): Anion=1;Cation=2

class Ion:
    def __init__(self,name,ionType,tests=[]):
        self.name = name
        self.tests = tests
        self.ionType = ionType
    def __repr__(self): return str(self)
    def __str__(self):
        return self.name;


