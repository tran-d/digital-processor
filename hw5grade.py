#!/usr/bin/python

# Auto Grader for Duke CS/ECE 250, Homework 5, Spring 2017

import sys,os,platform
from optparse import OptionParser

test_dir = 'grading_tests'
suite_names = ['dir_map_wb', 'dir_map_wt', 'set_assoc_wb', 'set_assoc_wt', 'full_assoc_wb', 'full_assoc_wt']
suites = {
    "dir_map_wb": [
        { "desc": "Write-back and write-allocate direct mapped cache", "args": ['tracefile_grading 8 1 wb 64'] },
    ],
    "dir_map_wt": [
        { "desc": "Write-through and write-no-allocate direct mapped cache", "args": ['tracefile_grading 8 1 wt 64'] },
    ],
    "set_assoc_wb": [
        { "desc": "Write-back and write-allocate set-associative cache", "args": ['tracefile_grading 32 8 wb 64'] },
    ],
    "set_assoc_wt": [
        { "desc": "Write-through and write-no-allocate set-associative cache", "args": ['tracefile_grading 32 8 wt 64'] },
    ],
    "full_assoc_wb": [
        { "desc": "Write-back and write-allocate fully-associative cache", "args": ['tracefile_grading 1 16 wb 64'] },
    ],
    "full_assoc_wt": [
        { "desc": "Write-through and write-no-allocate fully-associative cache", "args": ['tracefile_grading 1 16 wt 64'] },
    ],
}


parser = OptionParser("Usage: %prog <suite>")

if (len(sys.argv)<=1):
    print "\033[31;7mSelf Tester\033[m for Duke CS/ECE 250, Homework 5, Spring 2017"
    print ""
    parser.print_help()
    print ""
    print "Where <suite> is one of:"
    print "  %-15s: Run all program tests" % ("ALL",)
    print "  %-15s: Remove all the test output produced by this tool" % ("CLEAN",)
    for suite_name in suite_names:
        print "  %-15s: Run tests for %s." % (suite_name,suite_name)
    sys.exit(1)

def get_expected_output_filename(suite_name, test_num):
    return "%s/%s_expected_%d.txt" % (test_dir, suite_name, test_num)

def get_actual_output_filename(suite_name, test_num):
    return "%s/%s_actual_%d.txt" % (test_dir, suite_name, test_num)

def get_diff_filename(suite_name, test_num):
    return "%s/%s_diff_%d.txt" % (test_dir, suite_name, test_num)

def clean():
    my_system("rm -f "+test_dir+"/*_actual_*.txt", True)
    my_system("rm -f "+test_dir+"/*_diff_*.txt", True)
    my_system("rm -f *.class", True)

def verbose_print(s, verbose_mode):
    if verbose_mode: sys.stdout.write("\033[36m%s\033[m\n" % s)

def my_system(command, verbose_mode):
    verbose_print("$ %s" % command, verbose_mode)
    r = os.system(command)
    if platform.system()[-1] == 'x':
        return r>>8 # platforms ending in 'x' are probably Linux/Unix, and they put exit status in the high byte
    else:
        return r # windows platforms just return exit status directly

def run_test_suite(suite_name):
    executable = './cachesim'
    suite = suites[suite_name]
    if not os.path.isfile('cachesim'):
        executable = 'java cachesim'
        if not os.path.isfile('cachesim.java'):
            print "\033[91m%s: cachesim.java not found in current directory.\033[m" % (suite_name)
            return
        my_system("javac cachesim.java ", False)
    if not os.path.isfile('tracefile'):
        print "\033[91m%s: tracefile not found in current directory.\033[m" % (suite_name)
        return

    for test_num,test in enumerate(suite):
        desc = test['desc']
        args = test['args']
        expected_output_filename = get_expected_output_filename(suite_name, test_num)
        actual_output_filename = get_actual_output_filename(suite_name, test_num)
        diff_filename = get_diff_filename(suite_name, test_num)

	if not os.path.isfile(expected_output_filename):
            print "\033[91m%s: Expected output file not found in tests directory, expected: %s\033[m" % (suite_name, expected_output_filename)
            return

        is_pass = True
        reason = ''

        command = "timeout 30s %s %s > %s" % (executable, " ".join(args), actual_output_filename)
        r = my_system(command, False)
        if r != 0:
            is_pass = False
            reason += "Exit status is non-zero. "
	    if r == 124:
		reason += "Killed due to a timeout, infinite loop in the program? "

	command = "diff -bwB %s %s > %s" % (expected_output_filename, actual_output_filename, diff_filename)
	r = my_system(command, False)
	if r != 0 and is_pass == True:
            is_pass = False
            reason += "Output differs from expected (see diff for details). "

        if is_pass: result_string = "\033[32;7mpass\033[m"
        else:       result_string = "\033[41mFAIL\033[0;31m %s\033[m" % reason
        print "%10s test (%-45s): %s" % (suite_name, desc, result_string)

requested_suite_name = sys.argv[1]
if requested_suite_name == "ALL":
    for suite_name in suite_names:
        run_test_suite(suite_name)
elif requested_suite_name == "CLEAN":
    clean()
elif requested_suite_name in suite_names:
    run_test_suite(requested_suite_name)
else:
    print "%s: No such test suite" % (requested_suite_name)
