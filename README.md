# juju

<br>
<p align="center">
<img width="300px" src="./good_juju.png"/>
</p>

> [!CAUTION]
> This package is a rather simple and dumb idea, which probably has some sharp edges. Simple programs only for now! It's not yet clear _how much of JAX_ will be fully supported (and how many extensions via MAX kernels will be added).

This package supports a API called `max` whose purpose is to transform a _JAX computation_ into a [MAX computation graph](https://docs.modular.com/max). These graphs can then be executed using MAX.

**Example:**
```python
import jax.numpy as jnp
from juju import max

@max
def jax_code(x, y):
    v = x + y
    v = v * v
    return jnp.sin(v)

print(jax_code(5, 10).to_numpy()) # -0.93009484
```

The way this API works is that the computation is first staged to a `Jaxpr`, and then an interpreter is run. The interpreter traverses the `Jaxpr`, and replaces JAX primitives (like `jax.lax.add_p`) with ones from [MAX's operation set](https://docs.modular.com/max/api/mojo/graph/ops/).

In theory, one could define the JIT-like functionality that we've all come to know and love from JAX, using MAX as a backend in place of XLA.

> [!WARNING]
> You can't invoke these graphs _within a JAX computation which you `jax.jit`_ yet. In other words, you can't mix and max XLA and MAX in this package yet.

## MAX graphs

What is a MAX graph? Let's inspect one:

```python
import jax.numpy as jnp
from juju import max_graph

@max_graph
def jax_code(x, y):
    v = x + y
    v = v * v
    return jnp.sin(v)

print(jax_code(5, 10)) 
```

produces a textual object which looks like the following:

```
mo.graph @jax_code(%arg0: !mo.tensor<[], si32>, %arg1: !mo.tensor<[], si32>) -> !mo.tensor<[], f32> attributes {argument_names = ["input0", "input1"], result_names = ["output0"]} {
  %0 = mo.chain.create()
  %1 = rmo.add(%arg0, %arg1) : (!mo.tensor<[], si32>, !mo.tensor<[], si32>) -> !mo.tensor<[], si32>
  %2 = rmo.mul(%1, %1) : (!mo.tensor<[], si32>, !mo.tensor<[], si32>) -> !mo.tensor<[], si32>
  %3 = mo.cast(%2) : (!mo.tensor<[], si32>) -> !mo.tensor<[], f32>
  %4 = rmo.mo.sin(%3) : (!mo.tensor<[], f32>) -> !mo.tensor<[], f32>
  mo.output %4 : !mo.tensor<[], f32>
}
```

This is a MAX graph, an intermediate representation which can be fed to [MAX's execution engine](https://docs.modular.com/max/api/mojo/engine/) to perform computations.

## Composition with JAX transformations

Our approach is fully compositional with JAX transformations, meaning one can apply transformations like `jax.vmap` and `jax.grad` _before_ lowering the resulting computation to a MAX graph.

```python
from jax import grad
import jax.numpy as jnp
from juju import max

@max
@grad
def jax_code(x, y):
    v = x + y
    v = v * v
    return jnp.sin(v)


print(jax_code(5.0, 10.0).to_numpy()) # 11.019581
```

## JIT functionality

This package contains a very simple implementation of JIT functionality based on a JIT cache using [static Pytree structure](https://jax.readthedocs.io/en/latest/pytrees.html):

```python
from jax import grad
import jax.numpy as jnp
from juju import jit

@jit
def jax_code(x, y):
    v = x + y
    v = v * v
    return jnp.sin(v)

timing(jax_code)(5, 10) # 0.131628 s
timing(jax_code)(5, 10) # 0.000175 s 
```

The idea here is simple: a global MAX inference session is kept, and models are created and loaded into this session. We create a callable which executes these saved models, and we store this callable in a cache according to keys of the form `(your_hashable_callable, static_pytree_structure)`.

> [!WARNING]
> This is not nearly as featured as `jax.jit`. Indeed, some things you _cannot_ do with this now:
> * Invoke a `juju.jit` function inside of code which you want to lower to MAX.
> * No keyword arguments to specify static arguments.

## State of coverage of JAX primitives

Keep in mind, even if a primitive is supported by a test, there may be missing usage patterns which cause errors which we haven't covered yet.

- [X] `lax.add_p`
- [X] `lax.mul_p`
- [X] `lax.sin_p`
- [X] `lax.cos_p`
- [X] `lax.neg_p`
- [X] `lax.abs_p`
- [X] `lax.convert_element_type_p`
- [X] `ad_util.add_any_p`