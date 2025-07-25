from enum import Enum



class Enumerable(Enum):
    @classmethod
    def get(cls, key, default=None):
        try:
            return cls[key]
        except:
            return default

    @classmethod
    def get_value(cls, value, default=None):
        try:
            return cls(value)
        except:
            return default

    @classmethod
    def keys(cls):
        return list(x.name for x in cls)

    @classmethod
    def values(cls):
        return list(x.value for x in cls)

    def __str__(self):
        return self.name


class BaseImages(Enumerable):
    BOOKWORM = ('base', 'bookworm')
    BOOKWORM_SLIM = ('base', 'bookworm-slim')
    BUILDER = ('base', 'builder')
    BUSTER = ('base', 'buster')
    BUSTER_SLIM = ('base', 'buster-slim')

    @property
    def tag(self):
        return f'{self.value[0]}-{self.value[1]}'


class Languages(Enumerable):
    BASH = ('bash', ('5.2.15',), None, 'sh')
    BRAINFUCK = ('brainfuck', ('2.7.3',), None, 'bf')
    C = ('c', ('17.0.0',), None, 'c')
    COFFEESCRIPT = ('coffeescript', ('2.7.0',), None, 'coffee')
    COW = ('cow', ('1.0.0',), None, 'cow')
    C_PLUS_PLUS = ('cpp', ('20.0.0',), None, 'cpp')
    D = ('d', ('12.2.0',), None, 'd')
    DART = ('dart', ('2.19.2',), None, 'dart')
    DENO = ('deno', ('1.31.0',), None, 'ts')
    ELIXIR = ('elixir', ('1.14.3',), None, 'exs')
    EMOJI = ('emojicode', ('1.0.2',), None, 'emojic')
    ERLANG = ('erlang', ('25.3.0',), None, 'erl')
    FORTRAN = ('fortran', ('12.2.0',), None, 'f90')
    GOJQ = ('gojq', ('0.12.11',), None, 'jq')
    GOLANG = ('golang', ('1.20.1',), None, 'go')
#    GOLFSCRIPT = ('golfscript', ('1.0.0',), None, 'gs')
    JAVA = ('java', ('24.0.1',), None, 'java')
    LOLCODE = ('lolcode', ('0.11.2',), None, 'lol')
    LUA = ('lua', ('5.4.4',), None, 'lua')
    NASM = ('nasm', ('2.16.1',), None, 'asm')
    NASM_64 = ('nasm64', ('2.16.1',), None, 'asm')
    NODE = ('node', ('19.7.0', '21.1.0'), '21.1.0', 'js')
    PHP = ('php', ('8.2.3',), None, 'php')
    PROLOG = ('prolog', ('9.3.20',), None, 'pl')
    PYTHON = ('python', ('2.7.18', '3.9.16', '3.11.6', '3.12.0'), '3.11.6', 'py')
    PYTHON_2 = ('python', ('2.7.18',), None, 'py')
    RUBY = ('ruby', ('3.2.1',), None, 'rb')
    RUST = ('rust', ('1.67.1', '1.82.0'), '1.82.0', 'rs')
    SWIFT = ('swift', ('5.6.3',), None, 'swift')
    TYPESCRIPT = ('typescript', ('4.9.5', '5.0.0', '5.2.2'), '5.2.2', 'ts')

    @property
    def default_version(self):
        language, versions, default, extension = self.value
        return default or versions[0]

    @property
    def extension(self):
        return self.value[3]

    @property
    def language(self):
        return self.value[0]

    @property
    def versions(self):
        return self.value[1]

    def to_dict(self):
        return {
            'extension': self.extension,
            'default_version': self.default_version,
            'id': self.name,
            'language': self.language,
            'versions': [x for x in self.versions],
        }


LanguagePrepends = {
    Languages.ERLANG: '\n',
}
