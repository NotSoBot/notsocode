execute = (execute_with := lambda *a, **k: lambda f: f(*a, **k))()


@int
@execute
class n: __int__ = lambda _: 420


@execute
class cout: __lshift__ = print


@execute_with(n)
def output(n):
    return "Hello, World!"


cout << output