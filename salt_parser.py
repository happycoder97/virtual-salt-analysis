import configparser
import shlex
from enum import Enum

class Parser:
    anions = []
    cations = []

    def loadDataFromFile(self, filename, ion_type ):
        """ Load anion, cation data from an ini-like file """

        if type(ion_type) is not Ion.IonType:
            raise TypeError("Invalid ion_type: "+type(ion_type))
        cp = configparser.ConfigParser(delimiters=['='])
        cp.read(filename)

        for ion_name in cp:
            #foreach ['chloride'], ['sulphate'], ['ammonium'] etc
            ion = Ion(ion_name,ion_type,[])

            if ion_type == Ion.IonType.Anion: self.anions+=[ion]
            else: self.cations+=[ion]

            for test_action in cp[ion_name]:
                test_kwgs_raw = test_action.split(':')
                test_kwgs=[]
                # fmt: action keyword group 1 : group 2 : etc = result
                for kwg_raw in test_kwgs_raw:
                    test_kwgs += [shlex.split(kwg_raw)]

                test_rslt = cp[ion_name][test_action]

                # if the keywords begin with '..' then consider it as
                # a subtest of previous test
                # Note: currently only subtest of level 1 is supported
                if not test_kwgs[0][0] == '..':
                    ion.tests += [SaltTest(test_kwgs,test_rslt,[],None)] #TODO:sub_match
                else:
                    #TODO:sub_match
                    test_kwgs[0] = test_kwgs[0][1:]
                    ion.tests[-1].subtests += [SaltTest(test_kwgs,test_rslt,[],None)]

class Ion:
    class IonType(Enum): Anion=1;Cation=2
    def __init__(self,name,ionType,tests=[]):
        self.name = name
        self.tests = tests
        self.ionType = ionType
    def __repr__(self): return str(self)
    def __str__(self):
        return self.name;

class SaltTest:
    """ SaltTest class is intented to be owned by the Anion/Cation class.
        Keywords is a two-dimensional array of keywords
        to be matched for this test
        foreach subarray in keywords,
            foreach word in subarray, search for word
            then str=str[last:], where last is the greatest of indices
            where any word in subarray was found.
            This is to ensure that, in some tests some actions must be
            carried out strictly after the other.
            Like in brown ring test, H2SO4 should be added after FeSO4.
            At minimum, keywords should be [['FeSO4'],['H2SO4']]
            So str is chopped after the occurrence of FeSO4 and then
            searched for H2SO4. ie, str="Add H2SO4 then FeSO4" won't match
        result is the result to be output if the test is positive
        subtests is an array of other test to be carried out continuous to
        this test
        substitutions_matcher is a class that gives out possible alternative
        words for each keyword
    """

    def __init__(self,keywords,result,subtests,substitutions_matcher=None):
        self.keywords = keywords
        self.result = result
        self.subtests = subtests
        self.substitutions_matcher = substitutions_matcher

    def __repr__(self): return str(self)
    def __str__(self):
        s = ""
        for kwg in self.keywords:
            for kw in kwg:
                s+= kw+" "
            s+= " -> "
        s+=self.result
        if len(self.subtests) >0: s+="\n"
        for t in self.subtests:
            s+="\t"+str(t)
        return s


    def match(self,user_input_str):
        """ Searches the string user_input_str for keywords and subtests

            returns :
                True if test is matched completely and successfully.
                Another instance of test if some of the keywords or subtests
                are still remaining
                False if test failed to match any keywords

            Matching process is as follows:
                foreach 1D array in keywords, try to match the keywords.
                if atleast the first 1D array match successfully, but not all,
                then return a copy of self, with the matched 1D arrays removed.
                if all keywords succeed, then try with the list of subtests.
                like we did with keywords, try to match all and return a copy
                containing those subtests which failed
                if all subtests and keywords match successfully return true
                if no keywords were matched return false
        """

        def is_kw_in_str(kw,str):
            """ Check whether str contains kw, or any variations of kw
                provided by substitutions_matcher """
            if str.find(kw)!=-1: return True
            elif self.substitutions_matcher is not None:
                for sub in self.substitutions_matcher:
                    if user_input_str.find(sub) != -1: return True
            return False

        # TODO: return result
        if len(self.keywords)>0:
            for kw in self.keywords[0]:
                """ If the first group of keywords is not found in user_input_str
                    test is considered failed """
                if not is_kw_in_str(kw,user_input_str): return False,[]

            for i in range(1,len(self.keywords)):
                """ If any of the subsequent group of keywords are not found,
                    return a copy of this, with the successfully matched keyword group
                    removed from keywords list """
                for kw in self.keywords[i]:
                    if not is_kw_in_str(kw,user_input_str):
                        return SaltTest(keywords=self.keywords[i:],
                                result=self.result,
                                subtests=self.subtests,
                                substitutions_matcher=self.substitutions_matcher),[]
        result = [self.result]
        for i in range(len(self.subtests)):
            test = self.subtests[i]
            test_rslt, rslt_msg = test.match(user_input_str)
            if not test_rslt:
                return SaltTest(keywords=[], result=self.result,
                        subtests = self.subtests[i:],
                        substitutions_matcher = self.substitutions_matcher), result
            else: result+=rslt_msg
        return True, result
