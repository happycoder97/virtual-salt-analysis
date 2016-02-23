class KeywordGroup:

    def __init__(self,keywords,description):
        self.keywords = keywords
        self.description = description
    def __str__(self):
        return self.description

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

    def __init__(self,keyword_groups,result,subtests):
        self.keyword_groups = keyword_groups
        self.result = result
        self.subtests = subtests

    def __repr__(self):
        s=""
        for kwg in self.keyword_groups:
            s+=kwg.description+"->"
        s+=self.result
        for subtest in self.subtests: s+=" -> "+str(subtest)
        return s

