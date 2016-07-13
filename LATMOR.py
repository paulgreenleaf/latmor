#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this script should be run in the same directory as fst-infl latmor-gen.a
# words to be checked use [ä,ë,ï,ö,ü] for long vowels
# requires "prettytable" - https://code.google.com/p/prettytable/
# CIS : LATMOR - http://www.cis.uni-muenchen.de/~schmid/tools/LatMor/

import os
import sys
import subprocess
import re
from prettytable import PrettyTable
import argparse
from collections import OrderedDict
from LATMOR_PARADIGMS import * #the latin grammar is contained in these lists and dictionaries.

def split_lines(line_to_split): #cleans the transducer output.
	line_to_split = line_to_split.decode()
	pattern = re.compile('\n')
	split_list = pattern.split(line_to_split)
	clean_list = split_list[1:len(split_list)-1]
	return clean_list

def return_error_list(grammar, transducer): #produces the column showing where the transducer output does not match the paradigm.
	error_check = []
	for(entry_list_1, entry_list_2) in zip(grammar, transducer): 
		if entry_list_1 == entry_list_2:
			error_check.append("")
		else:
			error_check.append("*")
	return error_check

def table(trans_in, paradigm, trans_out, errors): #produces the output tables.
	table = PrettyTable()
	table.padding_width = 1
	table.add_column("Transducer Input",trans_in)
	table.add_column("Paradigm",paradigm)
	table.add_column("Transducer Output",trans_out)
	table.add_column("Errors",errors)
	return table

def err_table(transducer): #produces an error table; used in debugging.
	table = PrettyTable()
	table.padding_width = 1
	table.add_column("Transducer Output",transducer)
	return table

def make_regular(category): #produces the regular latin paradigms.
	guck_mal = []
	pruefen = []
	if category == 'adj':
		paradigm_from_grammar = REGULAR_ADJ_PARADIGM
		paradigm_var = ADJ_TRANS_VAR
	elif category == 'reg_noun':
		paradigm_from_grammar = REGULAR_NOUNS_PARADIGM
		paradigm_var = DECLENSIONS
	elif category == 'verb':
		paradigm_from_grammar = VERBS_PARADIGM

	for POS in paradigm_from_grammar:
		POS = POS.rstrip()
		paradigm_from_transducer = []
		transducer_input = []
		error_check = []
		try:
			for var in paradigm_var:
				var = var.rstrip()
				morphology = POS + var
				infl = subprocess.Popen("echo " + morphology + " | fst-infl latmor-gen.a", stdout=subprocess.PIPE, shell=True)			
				(inflOut, inflErr) = infl.communicate()
				inflStatus = infl.wait()
				paradigm_from_transducer.append(split_lines(inflOut))
				transducer_input.append(morphology)
			guck_mal.append(table(transducer_input,paradigm_from_grammar[POS],paradigm_from_transducer,return_error_list(paradigm_from_grammar[POS],paradigm_from_transducer)))
		except:
			pruefen.append(err_table(paradigm_from_transducer))
			pruefen.append(err_table(paradigm_from_grammar[POS]))

	for x in guck_mal:
		print(x)
	print("Something erred with these tables:")
	for x in pruefen:
		print(x)

def make_irregular(category): #produces the irregular latin paradigms.

	guck_mal = []
	pruefen = []
	paradigm_from_grammar = category

	for count, headword in enumerate(paradigm_from_grammar):
		morphology = paradigm_from_grammar.get(headword)[0]
		output_compare_list = paradigm_from_grammar.get(headword)[1]
		paradigm_from_transducer = []
		for m in morphology:
			m = ''.join(m)
			m = m.rstrip()
			infl = subprocess.Popen("echo " + m + " | fst-infl latmor-gen.a", stdout=subprocess.PIPE, shell=True)			
			(inflOut, inflErr) = infl.communicate()
			inflStatus = infl.wait()
			paradigm_from_transducer.append(split_lines(inflOut))
		try:
			guck_mal.append(table(morphology,output_compare_list,paradigm_from_transducer,return_error_list(output_compare_list,paradigm_from_transducer)))
		except:
			pruefen.append(err_table(output_compare_list))
			pruefen.append(err_table(paradigm_from_transducer))

	for x in guck_mal:
		print(x)
	print("Something erred with these tables:")
	for x in pruefen:
		print(x)

# arguments for selecting which parts of the grammar to check.
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--noun', help="Returns nouns.", action="store_true")
	parser.add_argument('--adj', help="Returns adjectives.", action="store_true")
	parser.add_argument('--pro', help="Returns pronouns.", action="store_true")
	parser.add_argument('--verb', help="Returns verbs.", action="store_true")
	parser.add_argument('--num', help="Returns numerals.", action="store_true")
	parser.add_argument('--adv', help="Returns postive, comparative, superlative forms.", action="store_true")
	parser.add_argument('--all', help="Returns everything.", action="store_true")

	args = parser.parse_args()
	if args.verb:
		print('*** VERBS ***')
		print(make_irregular(VERBS_PARADIGM))
		print(make_irregular(IRREGULAR_VERBS_PARADIGM))

	if args.noun:
		print('*** REGULAR NOUNS ***')
		print(make_regular('reg_noun'))
		print('*** IRREGULAR NOUNS ***')
		print(make_irregular(IRREGULAR_NOUNS_PARADIGM))

	if args.adj:
		print("*** ADJECTIVES ***")
		print(make_regular('adj'))

	if args.pro:
		print('*** PERSONAL PRONOUNS ***')
		print(make_irregular(PERSONAL_PRONOUNS))
		print('*** POSSESSIVE PRONOUNS ***')
		print(make_irregular(POSSESSIVE_PRONOUNS))
		print('*** RELATIVE PRONOUNS ***')
		print(make_irregular(RELATIVE_PRONOUNS))
		print('*** INTERROGATIVE PRONOUNS ***')
		print(make_irregular(INTERROGATIVE_PRONOUNS))
		print('*** INDEFINITE PRONOUNS ***')
		print(make_irregular(INDEFINITE_PRONOUNS))
		print('*** DEMONSTRATIVE PRONOUNS ***')
		print(make_irregular(DEMONSTRATIVE_PRONOUNS))

	if args.num:
		print('*** NUMERALS ***')
		print(make_irregular(NUMERALS))

	if args.adv:
		print('*** ADVERBS ***')
		print(make_irregular(ADVERBS))

	if args.all:
		print('*** VERBS ***')
		print(make_irregular(VERBS_PARADIGM))
		print(make_irregular(IRREGULAR_VERBS_PARADIGM))
		print('*** REGULAR NOUNS ***')
		print(make_regular('reg_noun'))
		print('*** IRREGULAR NOUNS ***')
		print(make_irregular(IRREGULAR_NOUNS_PARADIGM))
		print('*** PERSONAL PRONOUNS ***')
		print(make_irregular(PERSONAL_PRONOUNS))
		print('*** POSSESSIVE PRONOUNS ***')
		print(make_irregular(POSSESSIVE_PRONOUNS))
		print('*** RELATIVE PRONOUNS ***')
		print(make_irregular(RELATIVE_PRONOUNS))
		print('*** INTERROGATIVE PRONOUNS ***')
		print(make_irregular(INTERROGATIVE_PRONOUNS))
		print('*** INDEFINITE PRONOUNS ***')
		print(make_irregular(INDEFINITE_PRONOUNS))
		print('*** DEMONSTRATIVE PRONOUNS ***')
		print(make_irregular(DEMONSTRATIVE_PRONOUNS))
		print("*** ADJECTIVES ***")
		print(make_regular('adj'))
		print('*** ADVERBS ***')
		print(make_irregular(ADVERBS))
		print('*** NUMERALS ***')
		print(make_irregular(NUMERALS))


if __name__ == "__main__":
	main()