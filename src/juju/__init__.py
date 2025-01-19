from beartype import BeartypeConf
from beartype.claw import beartype_this_package

conf = BeartypeConf(
    is_color=True,
    is_debug=False,
    is_pep484_tower=True,
    violation_type=TypeError,
)

beartype_this_package(conf=conf)

from .compiler import make_max_graph, max_execute
from .jit import jit

__all__ = [
    "jit",
    "make_max_graph",
    "max_execute",
]
