import re
import inspect
from .pre_kaeru_parser import *

_escape_pattern = re.compile(r'&(?!#?\w+;)')
_newline_pattern = re.compile(r'\r\n|\r')
_pre_tags = ['pre', 'script', 'style']


def preprocessing(text, tab=4):
    text = _newline_pattern.sub('\n', text)
    text = text.expandtabs(tab)
    text = text.replace('\u2424', '\n')
    pattern = re.compile(r'^ +$', re.M)
    return pattern.sub('', text)


class Action:
    def __init__(self, name, entity):
        splitted_name = name.split('.')
        self.name = splitted_name[1]
        self.num = splitted_name[0]
        self.entity = entity


class Entity:
    def __init__(self, name):
        splitted_name = name.split('.')
        self.num = splitted_name[0]
        self.name = splitted_name[1]
        self.attribute = ''
        self.action_text = ''
        self.actions = []


class Grammar:
    entity = re.compile(r'^ *\[([^\n]+?)\] *(?:\n+|$)')
    partition = re.compile(r'^---(?:\n+|$)')
    next_entity = re.compile(r'^ *===> *([^\n]+?) *(?:\n+|$)')
    text = re.compile(r'^([^\n]+)')
    newline = re.compile(r'^\n+')

    GRAMMAR_LIST = (
        'entity', 'partition', 'next_entity', 'text', 'newline'
    )


class EndOfTokenException(Exception):
    pass


class Lexer:
    grammar_class = Grammar

    def __init__(self, grammar=None, **kwargs):
        self.tokens = []
        self.def_links = {}
        self.def_footnotes = {}

        if not grammar:
            grammar = self.grammar_class()

        self.grammar = grammar

    def __call__(self, text):
        return self.parse(text)

    def parse(self, text):
        self.full_text = text
        text = text.rstrip('\n')
        self.l = 0

        def manipulate(text):
            for grammar_name in self.grammar.GRAMMAR_LIST:
                grammar_rule = getattr(self.grammar, grammar_name)
                m = grammar_rule.match(text)
                if not m:
                    continue
                getattr(self, 'parse_%s' % grammar_name)(m)
                return m
            return False  # pragma: no cover

        while text:
            m = manipulate(text)
            if m is not False:
                text = text[len(m.group(0)):]
                continue
            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)
        return self.tokens

    def parse_newline(self, m):
        length = len(m.group(0))
        if length > 1:
            self.tokens.append({'type': 'newline', 'line': self.l})
        self.l += length

    def parse_entity(self, m):
        self.tokens.append({
            'type': 'entity_start',
            'text': m.group(1),
            'line': self.l
        })
        self.l += len(m.group(0))

    def parse_partition(self, m):
        self.tokens.append({
            'type': 'entity_separation',
            'line': self.l
        })
        self.l += len(m.group(0))

    def parse_next_entity(self, m):
        self.tokens.append({
            'type': 'next_entity',
            'text': m.group(1),
            'line': self.l
        })
        self.l += len(m.group(0))

    def parse_text(self, m):
        self.tokens.append({
            'type': 'text',
            'text': m.group(1),
            'line': self.l
        })
        self.l += len(m.group(0))


class Printer:
    def show_list(self, entity_table):
        for entity in entity_table.values():
            print('[{}]'.format(entity.name))
            for action in entity.actions:
                print('  {:10s} ===> [{:}]'.format(
                    action.name, action.entity.name))
            print()


class Compiler:
    lexer_class = Lexer
    initial_descriptor_values = {'temp': ''}

    def __init__(self, lexer=None, **kwargs):
        if not lexer:
            self.lexer = self.lexer_class()
        elif inspect.isclass(lexer):
            self.lexer = lexer(**kwargs)

        self.tokens = []
        self.entity_table = {}

        self.temp_text = ''

    def get_position(self):
        line = self.token['line']
        here = self.lexer.full_text[:line]
        here_split = here.split('\n')
        last_line_length = len(here_split[-1]) + 1
        which_line_num = len(here_split)
        return "L{}:C{}".format(which_line_num, last_line_length)

    def use_assigned_value(self):
        data = self.temp_text
        self.temp_text = ''
        return data

    def pop(self):
        if not self.tokens:
            raise EndOfTokenException()
        self.token = self.tokens.pop()
        return self.token

    def peek(self):
        if self.tokens:
            return self.tokens[-1]
        raise EndOfTokenException()

    def compile(self, text):
        text = preprocessing(text)

        self.tokens = self.lexer(text)
        self.tokens.reverse()

        try:
            while 1:
                self.pop()
                self.token_to_code()
        except EndOfTokenException:
            pass

    def token_to_code(self):
        t = self.token['type']

        # sepcial cases
        if t.endswith('_start'):
            t = t[:-6]

        return getattr(self, 'output_%s' % t)()

    def assign(self, text):
        if not self.entity_table:
            raise SyntaxError(
                "Entity does not exist, but it has symbol related to Entity.\n"
                "{}".format(self.get_position()))

        self.temp_text = (
            self.temp_text + '\n' + text
            if self.temp_text else text
        )

    def get_entity(self, name):
        exact_name = name.split('.')[1]
        entity = self.entity_table.get(exact_name)
        if not entity:
            entity = Entity(name=name)
            self.entity_table[exact_name] = entity
        return entity

    def output_entity(self):
        entity_name = self.token['text']
        self.entity = self.get_entity(name=entity_name)

        while self.peek()['type'] != 'entity_start':
            self.pop()
            self.token_to_code()

    def output_entity_separation(self):
        if self.entity.attribute:
            raise SyntaxError(
                "Attribute already exists for this entity. [{}]\n{}".format(
                    self.entity.name, self.get_position()))
        self.entity.attribute = self.use_assigned_value()

    def output_text(self):
        text = self.token['text']
        self.assign(text)

    def output_newline(self):
        self.assign('')

    def output_next_entity(self):
        next_entity_name = self.token['text']
        next_entity = self.get_entity(name=next_entity_name)
        self.entity.actions.append(
            Action(
                name=self.use_assigned_value(), entity=next_entity
            )
        )
