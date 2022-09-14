"""Implementation of arithmetic expression parsing."""
import ast
import operator as op
from typing import Any, Callable, Dict

import numpy as np

operator_map: Dict[Any, Callable] = {
    ast.USub: op.neg,
    ast.Sub: op.sub,
    ast.Add: op.add,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
}


def eval_expr(expr):
    return _eval_node(ast.parse(expr).body)


def _eval_node(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return operator_map[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operator_map[type(node.op)](_eval_node(node.operand))
    elif isinstance(node, ast.Name) and str(ast.Name) == "pi":
        return np.pi
    else:
        raise TypeError(node)
