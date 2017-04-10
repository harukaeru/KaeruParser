from kaeru_parser import Compiler, Printer
import sys

filename = sys.argv[1]
text = open(filename, 'r').read()
compiler = Compiler()
printer = Printer()

compiler.compile(text)
entity_table = compiler.entity_table
printer.show_list(entity_table)
