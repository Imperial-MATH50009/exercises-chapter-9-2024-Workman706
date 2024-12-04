"""package."""
import numbers
from functools import singledispatch


class Expression():
    """Expression."""

    def __init__(self, *operands):
        """initialize."""
        self.operands = operands

    def __eq__(self, other):
        """eq."""
        if not isinstance(other, type(self)):
            return False
        return self.operands == other.operands

    def __hash__(self):
        """hash."""
        return hash(self.operands)

    def __add__(self, other):
        """add."""
        if not isinstance(other, Expression):
            if other == 0:
                return self
            other = Number(other)
        if isinstance(other, Number) and isinstance(self, Number):
            return Number(self.value + other.value)
        if self == Number(0):
            return other
        if other == Number(0):
            return self
        return Add(self, other)

    def __radd__(self, other):
        """radd."""
        if not isinstance(other, Expression):
            if other == 0:
                return self
            other = Number(other)
        if isinstance(other, Number) and isinstance(self, Number):
            return Number(self.value + other.value)
        if self == Number(0):
            return other
        if other == Number(0):
            return self
        return Add(other, self)

    def __sub__(self, other):
        """sub."""
        if not isinstance(other, Expression):
            other = Number(other)
        if isinstance(other, Number) and isinstance(self, Number):
            return Number(self.value - other.value)
        return Sub(self, other)

    def __rsub__(self, other):
        """rsub."""
        if not isinstance(other, Expression):
            other = Number(other)
        if isinstance(other, Number) and isinstance(self, Number):
            return Number(self.other - other.self)
        return Sub(other, self)

    def __mul__(self, other):
        """mul."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Mul(self, other)

    def __rmul__(self, other):
        """rmul."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Mul(other, self)

    def __truediv__(self, other):
        """div."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Div(self, other)

    def __rtruediv__(self, other):
        """rdiv."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Div(other, self)

    def __pow__(self, other):
        """pow."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Pow(self, other)

    def __rpow__(self, other):
        """rpow."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Pow(other, self)


class Operator(Expression):
    """operator."""

    def __repr__(self):
        """repr."""
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        """str."""
        a = self.operands[0]
        b = self.operands[1]
        if a.level > self.level:
            a = f"({a!s})"
        else:
            a = str(a)
        if b.level > self.level:
            b = f"({b!s})"
        else:
            b = str(b)
        return f"{a} {self.opcode} {b}"


class Add(Operator):
    """add."""

    level = 3
    opcode = "+"


class Sub(Operator):
    """sub."""

    level = 3
    opcode = "-"


class Mul(Operator):
    """mul."""

    level = 2
    opcode = "*"


class Div(Operator):
    """div."""

    level = 2
    opcode = "/"


class Pow(Operator):
    """pow."""

    level = 1
    opcode = "^"


class Terminal(Expression):
    """terminal."""

    level = 0

    def __init__(self, value):
        """intialize."""
        super().__init__()
        self.value = value

    def __eq__(self, other):
        """eq."""
        if not isinstance(other, Terminal):
            return False
        return self.value == other.value

    def __hash__(self):
        """hash."""
        return hash(self.value)

    def __repr__(self):
        """repr."""
        return f"{type(self).__name__}({self.value})"

    def __str__(self):
        """str."""
        return str(self.value)


class Number(Terminal):
    """number."""

    def __init__(self, value):
        """intialize."""
        if isinstance(value, numbers.Number):
            super().__init__(value)
        else:
            raise TypeError


class Symbol(Terminal):
    """symbol."""

    def __init__(self, value):
        """initialize."""
        if isinstance(value, str):
            super().__init__(value)
        else:
            raise TypeError


def postvisitor(expr, fn, **kwargs):
    """postvisitor."""
    stack = []
    visited = {}
    stack.append(expr)
    while stack:
        texpr = stack.pop()
        unvis = [o for o in texpr.operands if o not in visited]
        if unvis:
            stack.append(texpr)
            stack += unvis
        else:
            difmap = [visited[o] for o in texpr.operands]
            visited[texpr] = fn(texpr, *difmap, **kwargs)
    return visited[expr]


@singledispatch
def differentiate(expr, *o, **kwargs):
    """differentiate."""
    raise NotImplementedError


@differentiate.register(Number)
def _(expr, *o, **kwargs):
    return Number(0)


@differentiate.register(Symbol)
def _(expr, *o, var, **kwargs):
    if expr.value == var:
        return Number(1)
    else:
        return Number(0)


@differentiate.register(Add)
def _(expr, *o, **kwargs):
    return o[0] + o[1]


@differentiate.register(Sub)
def _(expr, *o, **kwargs):
    return o[0] - o[1]


@differentiate.register(Mul)
def _(expr, *o, **kwargs):
    return expr.operands[0] * o[1] + expr.operands[1] * o[0]


@differentiate.register(Div)
def _(expr, *o, **kwargs):
    return (expr.operands[1] * o[0] - expr.operands[0] * o[1]) \
        / expr.operands[1]**2


@differentiate.register(Pow)
def _(expr, *o, **kwargs):
    if expr.operands[1] == Number(0):
        return expr.operands[1]
    else:
        return expr.operands[1] * expr.operands[0] ** \
            (expr.operands[1] - 1) * o[0]
