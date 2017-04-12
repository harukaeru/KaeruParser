import pytest
from kaeru_parser import Compiler


class TestClass:
    def setup_method(self, method):
        self.compiler = Compiler()

    def test_A(self):
        text = open('tests/A.txt', 'r').read()
        self.compiler.compile(text)
        entity_table = self.compiler.entity_table

        home = entity_table.get('Home')
        assert home.actions[0].name == 'click'
        assert home.actions[0].entity == entity_table.get("TodoList")
        assert home.actions[1].name == 'quit'
        assert home.actions[1].entity == entity_table.get("End")

        todo_list = entity_table.get('TodoList')
        assert todo_list.actions[0].name == "addTodo"
        assert todo_list.actions[0].entity == entity_table.get("TodoList")
        assert todo_list.actions[1].name == "removeTodo"
        assert todo_list.actions[1].entity == entity_table.get("TodoList")
        assert todo_list.actions[2].name == "back"
        assert todo_list.actions[2].entity == entity_table.get("Home")
        assert todo_list.actions[3].name == "quit"
        assert todo_list.actions[3].entity == entity_table.get("End")

        assert len(entity_table.items()) == 3

    def test_B(self):
        text = open('tests/B.txt', 'r').read()
        with pytest.raises(SyntaxError):
            self.compiler.compile(text)

    def test_C(self):
        text = open('tests/C.txt', 'r').read()
        with pytest.raises(SyntaxError):
            self.compiler.compile(text)

    def test_D(self):
        print("--- C ---")
        text = open('tests/D.txt', 'r').read()
        self.compiler.compile(text)
        entity_table = self.compiler.entity_table

        home = entity_table.get('Home')
        assert home.actions[0].name == 'click'
        assert home.actions[0].entity == entity_table.get("TodoList")
        assert home.actions[1].name == 'quit'
        assert home.actions[1].entity == entity_table.get("End")

        todo_list = entity_table.get('TodoList')
        assert todo_list.actions[0].name == "addTodo"
        assert todo_list.actions[0].entity == entity_table.get("TodoList")
        assert todo_list.actions[1].name == "removeTodo"
        assert todo_list.actions[1].entity == entity_table.get("TodoList")
        assert todo_list.actions[2].name == "back"
        assert todo_list.actions[2].entity == entity_table.get("Home")
        assert todo_list.actions[3].name == "quit"
        assert todo_list.actions[3].entity == entity_table.get("End")

        assert len(entity_table.items()) == 3
