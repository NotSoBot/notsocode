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
    BASH = ('bash', ('5.3.20',), None, 'sh')
    BRAINFUCK = ('brainfuck', ('2.7.3',), None, 'bf')
    BUN = ('bun', ('1.4.3',), None, 'ts')
    C = ('c', ('17.0.0', '23.0.0'), '23.0.0', 'c')
    COFFEESCRIPT = ('coffeescript', ('2.7.0',), None, 'coffee')
    COW = ('cow', ('1.0.0',), None, 'cow')
    C_PLUS_PLUS = ('cpp', ('20.0.0', '23.0.0'), '23.0.0', 'cpp')
    C_SHARP = ('csharp', ('10.0.13',), None, 'cs')
    D = ('d', ('16.2.0',), None, 'd')
    DART = ('dart', ('3.13.5',), None, 'dart')
    DENO = ('deno', ('2.9.7',), None, 'ts')
    ELIXIR = ('elixir', ('1.20.4',), None, 'exs')
    EMOJI = ('emojicode', ('1.0.2',), None, 'emojic')
    ERLANG = ('erlang', ('29.1.2',), None, 'erl')
    FORTRAN = ('fortran', ('16.2.0',), None, 'f90')
    GOJQ = ('gojq', ('0.12.19',), None, 'jq')
    GOLANG = ('golang', ('1.27.2',), None, 'go')
    GOLFSCRIPT = ('golfscript', ('1.0.0',), None, 'gs')
    JAVA = ('java', ('25.0.4', '27.0.0'), '27.0.0', 'java')
    KOTLIN = ('kotlin', ('2.4.21',), None, 'kt')
    LOLCODE = ('lolcode', ('1.3.0',), None, 'lol')
    LUA = ('lua', ('5.4.9', '5.5.1'), '5.5.1', 'lua')
    NASM = ('nasm', ('3.2.0',), None, 'asm')
    NASM_64 = ('nasm64', ('3.2.0',), None, 'asm')
    NODE = ('node', ('22.23.3', '24.22.0', '26.12.1'), '24.22.0', 'js')
    PERL = ('perl', ('5.44.0',), None, 'pl')
    PHP = ('php', ('8.5.11',), None, 'php')
    PROLOG = ('prolog', ('10.0.2',), None, 'pl')
    PYTHON = ('python', ('2.7.18', '3.11.17', '3.12.15', '3.13.16', '3.14.8'), '3.14.8', 'py')
    PYTHON_2 = ('python', ('2.7.18',), None, 'py')
    RUBY = ('ruby', ('4.0.7',), None, 'rb')
    RUST = ('rust', ('1.99.1',), None, 'rs')
    SQLITE_3 = ('sqlite3', ('3.54.1',), None, 'sql')
    SWIFT = ('swift', ('6.4.1',), None, 'swift')
    TYPESCRIPT = ('typescript', ('7.0.2',), None, 'ts')

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
