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
    BUILDER = ('base', 'builder')
    BUSTER = ('base', 'buster')
    BUSTER_SLIM = ('base', 'buster-slim')

    @property
    def tag(self):
        return f'{self.value[0]}-{self.value[1]}'


class Languages(Enumerable):
    BASH = ('bash', ('5.2.15',), None, 'sh')
    COW = ('cow', ('1.0.0',), None, 'cow')
    DART = ('dart', ('2.19.2',), None, 'dart')
    DENO = ('deno', ('1.31.0',), None, 'ts')
    EMOJI = ('emojicode', ('1.0.2',), None, 'emojic')
    GOLANG = ('golang', ('1.20.1',), None, 'go')
    LUA = ('lua', ('5.4.4',), None, 'lua')
    NODE = ('node', ('19.7.0',), None, 'js')
    PHP = ('php', ('8.2.3',), None, 'php')
    PYTHON = ('python', ('2.7.18', '3.9.16', '3.11.2'), '3.9.16', 'py')
    PYTHON_2 = ('python', ('2.7.18',), None, 'py')
    RUBY = ('ruby', ('3.2.1',), None, 'rb')
    RUST = ('rust', ('1.67.1',), None, 'rs')
    SWIFT = ('swift', ('5.6.3',), None, 'swift')
    TYPESCRIPT = ('typescript', ('4.9.5', '5.0.0'), None, 'ts')

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



HTTP_STATUS_CODES = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",  # see RFC 8297
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi Status",
    208: "Already Reported",  # see RFC 5842
    226: "IM Used",  # see RFC 3229
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Switch Proxy",  # unused
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",  # unused
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",  # see RFC 2324
    421: "Misdirected Request",  # see RFC 7540
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",  # see RFC 8470
    426: "Upgrade Required",
    428: "Precondition Required",  # see RFC 6585
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    449: "Retry With",  # proprietary MS extension
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",  # see RFC 2295
    507: "Insufficient Storage",
    508: "Loop Detected",  # see RFC 5842
    510: "Not Extended",
    511: "Network Authentication Failed",
}
