import re
import inspect

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
    def __init__(self, name):
        self.name = name
        self.entity = None


class Entity:
    def __init__(self, name):
        self.name = name
        self.attribute = ''
        self.actions = []

    def set_action(self, name):
        self.action = Action(name=name)


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
        text = text.rstrip('\n')

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
            self.tokens.append({'type': 'newline'})

    def parse_entity(self, m):
        self.tokens.append({
            'type': 'entity_start',
            'text': m.group(1),
        })

    def parse_partition(self, m):
        self.tokens.append({
            'type': 'entity_separation',
        })

    def parse_next_entity(self, m):
        self.tokens.append({
            'type': 'next_entity',
            'text': m.group(1),
        })

    def parse_text(self, m):
        self.tokens.append({
            'type': 'text',
            'text': m.group(1)
        })


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

    def __init__(self, lexer=None, **kwargs):
        if not lexer:
            self.lexer = Lexer()
        elif inspect.isclass(lexer):
            self.lexer = lexer(**kwargs)

        self.tokens = []
        self.entity_table = {}

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

    def assign(self, data):
        assign = getattr(*self.state)
        if inspect.ismethod(assign) or inspect.ismethod(assign):
            assign(data)
            return

        if assign:
            assign = assign + '\n' + data
        else:
            assign = data
        setattr(*(self.state + (data,)))

    def get_entity(self, name):
        entity = self.entity_table.get(name)
        if not entity:
            entity = Entity(name=name)
            self.entity_table[name] = entity
        return entity

    def output_entity(self):
        entity_name = self.token['text']
        self.entity = self.get_entity(name=entity_name)

        self.state = (self.entity, 'attribute')

        while self.peek()['type'] != 'entity_start':
            self.pop()
            self.token_to_code()

    def output_entity_separation(self):
        self.state = (self.entity, 'set_action')

    def output_text(self):
        text = self.token['text']
        self.assign(text)

    def output_newline(self):
        self.assign('\n')

    def output_next_entity(self):
        next_entity_name = self.token['text']
        next_entity = self.get_entity(name=next_entity_name)
        self.entity.action.entity = next_entity
        self.entity.actions.append(self.entity.action)
        self.entity.action = None
