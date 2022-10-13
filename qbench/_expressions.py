"""Implementation of arithmetic expression parsing."""
import ast
import operator as op
from functools import singledispatch
from typing import Any, Callable, Dict

import numpy as np

operator_map: Dict[Any, Callable] = {
    ast.USub: op.neg,
    ast.Sub: op.sub,
    ast.Add: op.add,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
}


def eval_expr(expr: str) -> float:
    """Evaluate given arithmetic expression.

    :param expr: arithmetic expression to parse. The expression can contain parentheses,
     numbers, binary operators - + * /, unary minus and an identifier "pi". The "pi"
     identifier will resolve into numpy.py.
    :return: value of the evaluated expression.
    """
    return _eval_node(ast.parse(expr, mode="eval").body)


@singledispatch
def _eval_node(node):
    raise TypeError(f"Unsupported node type {type(node)}")


@_eval_node.register
def _eval_number(node: ast.Constant):
    return node.value


@_eval_node.register
def _eval_binary_operator(node: ast.BinOp):
    return operator_map[type(node.op)](_eval_node(node.left), _eval_node(node.right))


@_eval_node.register
def _eval_unary_operator(node: ast.UnaryOp):
    return operator_map[type(node.op)](_eval_node(node.operand))


@_eval_node.register
def _eval_name(node: ast.Name):
    if node.id == "pi":
        return np.pi
    raise ValueError(f"Unknown name: {node.id}")
