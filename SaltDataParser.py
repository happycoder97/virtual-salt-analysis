import configparser
import shlex
import re
from enum import Enum

from SaltTest import SaltTest, KeywordGroup
from Ion import Ion,IonType

class Parser:
    anions = []
    cations = []

    def loadDataFromFile(self, filename: str, ion_type: IonType ):
        """ Load anion, cation data from an ini-like file """

        if type(ion_type) is not IonType:
            raise TypeError("Invalid ion_type: "+type(ion_type))
        cp = configparser.ConfigParser(delimiters=['='])
        cp.optionxform = lambda x:x
        cp.read(filename)

        for ion_name in cp:
            if ion_name == "DEFAULT": continue
            #foreach ['chloride'], ['sulphate'], ['ammonium'] etc
            ion = Ion(ion_name,ion_type,[])

            if ion_type == IonType.Anion: self.anions+=[ion]
            else: self.cations+=[ion]

            for test_action in cp[ion_name]:
                test_kwgs_raw = test_action.split(':')
                test_kwgs = []
                # fmt: description [keyword] group 1 : group 2 : etc = result
                for kwg_raw in test_kwgs_raw:
                    # strip brackets off the description
                    description = re.sub(pattern=r'[{}]',repl="",string=kwg_raw)
                    # regex to find all those (kws) with brackets excluded
                    kws = re.findall(r'\{(.+?)\}',kwg_raw)
                    test_kwgs += [KeywordGroup(kws, description)]

                test_rslt = cp[ion_name][test_action]

                # if the description begin with '..' then consider it as
                # a subtest of previous test
                # Note: currently only subtest of level 1 is supported
                if not test_kwgs[0].description.startswith(".."):
                    ion.tests += [SaltTest(test_kwgs,test_rslt,[])] #TODO:sub_match
                else:
                    #TODO:sub_match
                    test_kwgs[0].description = test_kwgs[0].description[2:]
                    ion.tests[-1].subtests += [SaltTest(test_kwgs,test_rslt,[])]
        # for (ion,test) in [(ion,ion.tests) for ion in (self.cations if ion_type==IonType.Cation else self.anions)]:
            # print(ion.name+":"+str(test))
