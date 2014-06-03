class SwitchCase:

    """
    Simple implementation of switch-case statements in Pythonic style.

        >>> switch = SwitchCase()

    Adding case handlers:

        >>> @switch.case('foo')
        ... def foo():
        ...     print('foo')
        >>> @switch.case('bar')
        ... def bar():
        ...     print('bar')

    Default handler:

        >>> @switch.case()
        ... def baz():
        ...     print('baz')

    Use:

        >>> switch('foo')
        foo
        >>> switch('bar')
        bar
        >>> switch(42)
        baz

    """

    __slots__ = ['handlers', 'default']

    def __init__(self):
        self.handlers = dict()
        self.default = None

    def __call__(self, arg):
        x = self.handlers.get(arg, self.default)
        if x is not None:
            x()

    def case(self, param=None):
        if param is not None:
            def case_adder(handler):
                self.handlers[param] = handler
        else:
            def case_adder(handler):
                self.default = handler
        return case_adder


class SwitchCaseNames(SwitchCase):

    """
    SwitchCase subclass with namespace support via dicts.

        >>> switch = SwitchCaseNames()
        >>> @switch.case('foo')
        ... def foo(names):
        ...     names['foo'] = 'bar'
        >>> names = dict()
        >>> switch('foo', names)
        >>> print(names['foo'])
        bar

    """

    def __call__(self, arg, names):
        x = self.handlers.get(arg, self.default)
        if x is not None:
            x(names)
