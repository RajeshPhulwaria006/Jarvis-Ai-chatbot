import ast
import math
import operator
from fractions import Fraction
from langchain_core.tools import tool

# Allowed arithmetic operators
BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Allowed mathematical functions
FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "factorial": math.factorial,
    "ceil": math.ceil,
    "floor": math.floor,
    "abs": abs,
}


@tool
def math_calculator(expression: str) -> str:
    """Calculate a mathematical expression deterministically.

    Use for arithmetic, nested expressions, powers, modulo,
    square roots, trigonometry, logarithms, and factorials.
    Use radians for trigonometric functions.
    Enter a valid Python-style mathematical expression.
    Never estimate the result yourself.
    """
    try:
        result = safe_calculate(expression)
        return f"Exact computed result: {result!r}"
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError,
            OverflowError) as exc:
        return f"CALCULATION_ERROR: {type(exc).__name__}: {exc}"


def safe_calculate(expression: str):
    if not expression or len(expression) > 2000:
        raise ValueError("Expression must contain 1–2000 characters.")

    tree = ast.parse(expression, mode="eval")

    # Bound AST complexity.
    nodes = list(ast.walk(tree))
    if len(nodes) > 300:
        raise ValueError("Expression is too complex.")

    return calculate_node(tree)

def calculate_node(node):
    """Evaluate only explicitly permitted AST nodes."""

    if isinstance(node, ast.Expression):
        return calculate_node(node.body)

    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("Only numeric constants are allowed.")

        if isinstance(node.value, float) and not math.isfinite(node.value):
            raise ValueError("Non-finite numbers are not allowed.")

        return node.value

    if isinstance(node, ast.BinOp):
        operation = BINARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported arithmetic operator.")

        left = calculate_node(node.left)
        right = calculate_node(node.right)

        if isinstance(node.op, ast.Pow):
            if abs(right) > 10000:
                raise ValueError("Exponent exceeds the allowed limit.")

        if isinstance(node.op, ast.Mult):
            # Bound integer growth before multiplication.
            if (
                isinstance(left, int)
                and isinstance(right, int)
                and left.bit_length() + right.bit_length() > 100000
            ):
                raise ValueError("Result would be too large.")

        result = operation(left, right)
        return validate_result(result)

    if isinstance(node, ast.UnaryOp):
        operation = UNARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported unary operator.")

        return validate_result(operation(calculate_node(node.operand)))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct math function calls are allowed.")

        function = FUNCTIONS.get(node.func.id)

        if function is None:
            raise ValueError(f"Unsupported function: {node.func.id}")

        if node.keywords:
            raise ValueError("Keyword arguments are not supported.")

        args = [calculate_node(arg) for arg in node.args]

        if node.func.id == "factorial":
            if len(args) != 1 or type(args[0]) is not int:
                raise ValueError("factorial requires one integer.")

            if not 0 <= args[0] <= 10000:
                raise ValueError("Factorial input must be between 0 and 10000.")

        if node.func.id in {"sqrt", "log", "log10"}:
            if not args or args[0] < 0:
                if node.func.id == "sqrt" and args and args[0] == 0:
                    pass
                else:
                    raise ValueError("Invalid real-number function input.")

        return validate_result(function(*args))

    raise ValueError(
        f"Unsupported expression component: {type(node).__name__}"
    )


def validate_result(value):
    """Reject non-finite and excessively large results."""

    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Result is undefined or non-finite.")

    if isinstance(value, int) and value.bit_length() > 100000:
        raise ValueError("Result exceeds the supported size.")

    return value