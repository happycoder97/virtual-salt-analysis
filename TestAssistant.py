from fuzzywuzzy import process as fuzzyprocess
import itertools

class TestProgress:

    def __init__(self,test):
        self.test = test
        self.matched_keyword_groups = []
        self.completed_subtests = []

    def __repr__(self):
        s = ""
        for kwg in self.matched_keyword_groups:
            s+=kwg.description+"->"
        # ??? May be list equality won't work in python
        s+=self.test.result if (self.matched_keyword_groups ==
                self.test.keyword_groups) else " ??? "
        for subtest in self.completed_subtests:
            s+=" -> "+str(subtest)
        return s

class TestAssistant:

    def __init__(self,substitutions_list=None):
        self.test_progress_dict = {}
        self.substitutions_list = substitutions_list
    def has_test_fully_completed(self,test):
        if test not in self.test_progress_dict:
            return False

        test_progress = self.test_progress_dict[test]
        return (len(test_progress.matched_keyword_groups) ==
                len(test.keyword_groups) and
                len(test_progress.completed_subtests) == len(test.subtests))



    def try_match(self,test,user_input_str):

        test_progress = TestProgress(test)

        if test not in self.test_progress_dict:
            self.test_progress_dict[test] = test_progress

        chop_at = 0

        for kw in test.keyword_groups[0].keywords:
            """ If the first group of keywords is not found in user_input_str
                test is considered failed """
            kw_i = self._find_kw_in_str(kw,user_input_str)
            if kw_i==-1: return False
            chop_at = max(kw_i+len(kw),chop_at)

        test_progress.matched_keyword_groups+=[test.keyword_groups[0]]
        user_input_str = user_input_str[chop_at:]

        for kwg in test.keyword_groups[1:]:

            if (len(test_progress.matched_keyword_groups)>
                    len(self.test_progress_dict[test].matched_keyword_groups)):
                self.test_progress_dict[test] = test_progress
            for kw in kwg.keywords:
                kw_i = self._find_kw_in_str(kw,user_input_str)
                if kw_i==-1: return test_progress
                chop_at = max(kw_i+len(kw),chop_at)
            test_progress.matched_keyword_groups+=[kwg]

            user_input_str = user_input_str[chop_at:]

        if (len(test_progress.matched_keyword_groups)>
                len(self.test_progress_dict[test].matched_keyword_groups)):
            self.test_progress_dict[test] = test_progress

        for subtest in test.subtests:
            # !!! Possible bug when subtest is partially matched.
            # With current data, it seems like there won't be any problem
            res = self.try_match(subtest,user_input_str)
            if res:
                test_progress.completed_subtests+=[subtest]
            else:
                # !!! If a test with no keywords, but only subtests are
                # introduced, this code will break
                return test_progress

            if (len(test_progress.completed_subtests)>
                    len(self.test_progress_dict[test].completed_subtests)):
                self.test_progress_dict[test] = test_progress
        return True

    def try_continue_match(self,test_progress,user_input_str):
        # test_progress = self.test_progress_dict[test]
        test = test_progress.test
        for kwg in test.keyword_groups:

            if kwg in test_progress.matched_keyword_groups:
                continue
            chop_at = 0
            for kw in kwg.keywords:
                kw_i = self._find_kw_in_str(kw,user_input_str)
                if kw_i==-1: return test_progress
                chop_at = max(kw_i+len(kw),chop_at)
            test_progress.matched_keyword_groups+=[kwg]
            user_input_str = user_input_str[chop_at:]

            if (len(test_progress.matched_keyword_groups)>
                    len(self.test_progress_dict[test].matched_keyword_groups)):
                self.test_progress_dict[test] = test_progress

        for subtest in test.subtests:
            # !!! Possible bug when subtest is partially matched.
            # With current data, it seems like there won't be any problem
            res = self.try_match(subtest,user_input_str)
            if res:
                test_progress.completed_subtests+=[subtest]
            else:
                # !!! If a test with no keywords, but only subtests are
                # introduced, this code will break
                return test_progress

            if (len(test_progress.completed_subtests)>
                    len(self.test_progress_dict[test].completed_subtests)):
                self.test_progress_dict[test] = test_progress
        return True

    def _find_kw_in_str(self,kw,string):
        """ Check whether string contains kw, or any variations of kw
            provided by substitutions_list """
        def _n_at_a_time_gen(list,n):
            for i,v in enumerate(list):
                if i < len(list):
                    yield [l for l in list[i:i+n]]

        if len(string)==0:
            return -1

        kw = kw.lower()
        string = string.lower()
        match,rate = fuzzyprocess.extractOne(
                kw, (" ".join(sl) for sl in _n_at_a_time_gen(string.split(),len(kw.split()))
                ))
        # if rate>80:
            # print(" %2f %% %s " % (rate,match))
        if rate>90:
            return string.find(match)
        elif self.substitutions_list is not None:
            # split and substitute for cases like dil. HCl
            orig_kws = kw.split()
            # print("orig-kkws:"+str(orig_kws))
            has_substitutions = list(itertools.filterfalse(
                    lambda kw:kw not in self.substitutions_list,
                    orig_kws))
            # print("has_sub:"+str(has_substitutions))
            if len(has_substitutions)==0 :
                return -1
            substitutions = []
            substitutions+= [ ([kw]+self.substitutions_list[kw]\
                    if kw in self.substitutions_list else [kw])\
                    for kw in orig_kws]
            # print(substitutions)
            # [:1] to exclude first element which is just the original one that was passed
            substitution_combs = list(itertools.product(*substitutions))[1:]
            print(substitution_combs)
            for sub in substitution_combs:
                i = self._find_kw_in_str(" ".join(sub),string)
                if i!=-1: return i
        return -1

