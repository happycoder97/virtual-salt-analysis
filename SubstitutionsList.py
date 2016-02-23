import configparser
from CaseInsensitiveDict import CaseInsensitiveDict

class SubstitutionsList(CaseInsensitiveDict):

    def load_from_file(self,filename):
        file = open(filename,'r')
        for line in file:
            kw,*subs = [s.strip() for s in line.split('=')]
            if kw in self:
                self[kw]+=subs
            else:
                self[kw] = subs

