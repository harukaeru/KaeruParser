# kaeru_parser
## Concept
`kaeru_parser` is the converter guiflow-markdown format to python class has relations.

You can use them to create DB Table that also has relations, and etc...

## What is Guiflow?
Here is the link to Guiflow

https://github.com/hirokidaichi/guiflow

## Usage
If there is a file named _foo.txt_,
```markdown
[Home]
click
===> TodoList
quit
===> End

[TodoList]
addTodo
===> TodoList
removeTodo
===> TodoList
back
===> Home
quit
===> End
```

You can parse and convert such as the followings.

```python
>>> from kaeru_parser import add_numbers
>>> print(add_numbers('foo.txt'))
[2.Home]
10006.click
===> 3.TodoList
10007.quit
===> 1.End

[3.TodoList]
10004.addTodo
===> 3.TodoList
10008.removeTodo
===> 3.TodoList
10005.back
===> 2.Home
10007.quit
===> 1.End

>>> numbered = add_numbers('foo.txt')
>>> from kaeru_parser import Compiler
>>> compiler = Compiler()
>>> compiler.compile(numbered)
>>> compiler.entity_table
{'Home': <kaeru_parser.Entity object at 0x11041f518>, 'TodoList': <kaeru_parser.Entity object at 0x11041f588>, 'End': <kaeru_parser.Entity object at 0x11041f710>}
>>> home_entity = compiler.entity_table['Home']
>>> home_entity.num
'2'
>>> home_entity.name
'Home'
>>> home_entity.actions
[<kaeru_parser.Action object at 0x11041f630>, <kaeru_parser.Action object at 0x11041f780>]
>>> click_action = home_entity.actions[0]
>>> click_action.num
'10006'
>>> click_action.name
'click'
>>> click_action.entity
<kaeru_parser.Entity object at 0x11041f588>
>>> click_action.entity.name
'TodoList'
>>> from kaeru_parser import Printer
>>> printer = Printer()
>>> printer.show_list(compiler.entity_table)
[Home]
  click      ===> [TodoList]
  quit       ===> [End]

[TodoList]
  addTodo    ===> [TodoList]
  removeTodo ===> [TodoList]
  back       ===> [Home]
  quit       ===> [End]

[End]

```

If you want to know more, run `py.test` command for test and then go to `tests` directory.
