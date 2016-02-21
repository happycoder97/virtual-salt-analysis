#!/bin/python



# TODO:: :)
def string_diff(str1,str2):
    """ Returns a number which represents how different str1 is from str2
        Points:
            Missing of n letters: n points (apple vs aple: 1)
            Disorder of n letters: n points (back vs bcak: 1)
            TODO: Interchange of similar consonant groups: (tion vs sion: 1)
    """

    similar_sounds = {
            'tion' : 'sion'
            'a' : 'e'
            'ie' : 'ei'
            'oo' : 'u'
            'i' : 'y'
            'er' : 're'
            'full' : 'ful'
            'ake' : 'ike'
            }

    # identifiable idnetfiabel
    i = 0
    
    # Find first occurrence of dissimilarity
    while str1[i] == str2[i]: i++

    max_advance = 5

    # Try to advance till max_advance to find similarity




