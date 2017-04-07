from kaeru_parser import Compiler, Printer

text = open('/Users/usrNeko/work/goocus3-android/app/Android_flow_english.txt', 'r').read()
compiler = Compiler()
printer = Printer()

compiler.compile(text)
entity_table = compiler.entity_table
printer.show_list(entity_table)

print(entity_table['main_home'].attribute)
