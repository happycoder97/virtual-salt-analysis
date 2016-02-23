import readline
from random import randint
from fuzzywuzzy import fuzz
from SaltDataParser import Parser
from TestAssistant import TestAssistant, TestProgress
from SubstitutionsList import SubstitutionsList
from Ion import IonType
import itertools
import time

DEBUG = False

def debug(str):
    if not DEBUG: return
    print("DEBUG: %s " % str)

def main():
    print("--- Virtual Salt Analysis ---",end='\n'*2)
    print("Commands:")
    print("  Run tests - Type the procedure just like in your textbook")
    print("    You only need to type the important keywords correctly")
    print("    ie, name of reagents, heat or boil, etc")
    print("    Other words are intelligently recognized by the program")
    print("  Submit your answer - submit cation anion")
    print("    eg: submit Barium Chloride")
    print("  Exit the program - exit or press twice Ctrl+C or Ctrl+D")
    print()
    print("Loading anions and cations ..")

    parser = Parser()
    parser.loadDataFromFile('anions.ini',IonType.Anion)
    parser.loadDataFromFile('cations.ini',IonType.Cation)

    print("Choosing a cation and an anion at random ..")
    anion = parser.anions[randint(0,len(parser.anions)-1)]
    cation = parser.cations[randint(0,len(parser.cations)-1)]


    debug("%s %s" % (cation.name,anion.name))

    print("Loading alternate vocabulary ..")
    substitutions_list = SubstitutionsList()
    substitutions_list.load_from_file('substitutions.ini')

    test_assistant = TestAssistant(substitutions_list)

    tests = anion.tests+cation.tests

    print("\nReady!")
    pending_test = None

    guessed_salt = ""
    
    last_ctrl_c = 0
    while True:
        if pending_test == None:
            try:
                user_input_str = input("--> ")
            except (KeyboardInterrupt, EOFError):
                if time.time() - last_ctrl_c >2:
                    last_ctrl_c = time.time()
                    print("Press again to exit.")
                    continue
                else:
                    break

            if user_input_str.startswith("submit"):
                guessed_salt = " ".join(user_input_str.split()[1:])
                break

            if user_input_str == "exit":
                print("Exiting..")
                return 0

            if len(user_input_str)==0 : continue
            for test in tests:
                result = test_assistant.try_match(test,user_input_str)
                if result == True:
                    # debug("result=True")
                    print(test)
                    break
                elif result == False:
                    # debug("result=False")
                    continue
                else:
                    pending_test = result
                    print(pending_test)
                    break
            else:
                print("Nothing characteristic")

        else:
            user_input_str = input("and? > ")
            if len(user_input_str) == 0 :
                pending_test = None
                continue
            result = test_assistant.try_continue_match(pending_test,user_input_str)
            if result == True:
                print(pending_test)
                pending_test = None
                continue
            elif result == False:
                pending_test = None
                continue
            else:
                print(pending_test)

    print()
    print("Results:")
    actual_salt = "%s %s" % (cation.name,anion.name)
    if fuzz.ratio(actual_salt.lower(),guessed_salt.lower())>95:
        print("Congratulations! ",end="")
    else:
        print("Sorry! ",end="")

    print("The salt was "+actual_salt)

    completed_tests_cation = [ test for test in cation.tests\
            if test_assistant.has_test_fully_completed(test) ]
    partially_completed_tests_cation = [ test for test in cation.tests\
            if test in test_assistant.test_progress_dict and\
            not test_assistant.has_test_fully_completed(test) ]
    remaining_tests_cation = [test for test in cation.tests\
            if test not in test_assistant.test_progress_dict ]

    completed_tests_anion = [ test for test in anion.tests\
            if test_assistant.has_test_fully_completed(test) ]
    partially_completed_tests_anion = [ test for test in anion.tests\
            if test in test_assistant.test_progress_dict and\
            not test_assistant.has_test_fully_completed(test) ]
    remaining_tests_anion = [test for test in anion.tests\
            if test not in test_assistant.test_progress_dict ]

    if not partially_completed_tests_anion and not remaining_tests_anion\
        and not partially_completed_tests_cation and not remaining_tests_cation:
        print("You have successfully completed all analysis.")
    else:
        print("Oops! Seems like you have missed some tests..")

    def print_summary(title,anion_tests,cation_tests):
        if anion_tests or cation_tests:
            print()
            print("Summary of %s Tests:" % title)

            if anion_tests:
                print_wrap_indent("Anions:",preindent=' '*2)
                for test in anion_tests:
                    print_wrap_indent(str(test))

            if cation_tests:
                print_wrap_indent("Cations:",preindent=' '*2)
                for test in cation_tests:
                    print_wrap_indent(str(test))

    print_summary("Remaining",remaining_tests_anion,remaining_tests_cation)
    print_summary("Partially Completed",partially_completed_tests_anion,partially_completed_tests_cation)
    print_summary("Completed",completed_tests_anion,completed_tests_cation)

def print_wrap_indent(long_string,width=-1,newline='\n',indentation=' '*6,preindent=' '*4):
    import textwrap
    if width==-1:
        import shutil
        width = shutil.get_terminal_size()[0]
    print(preindent,end='')
    print((newline).join(
        textwrap.wrap(long_string,width-len(indentation))).replace(newline,newline+indentation)
        )

if __name__=="__main__":
    main()
