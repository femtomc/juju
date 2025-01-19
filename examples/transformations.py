import jax.numpy as jnp
from jax import vmap

from juju import jit


def f(x):
    return x**2


print(jit(vmap(f))(jnp.array([1.0, 2.0, 3.0])))
