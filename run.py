from kaeru_parser import Compiler, Printer

text = open('../Android_flow.txt', 'r').read()
compiler = Compiler()
printer = Printer()

compiler.compile(text)
entity_table = compiler.entity_table
printer.show_list(entity_table)
