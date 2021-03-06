# coding=utf-8
# Copyright 2020 The Trax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Layers that compute activation functions.

An activation layer computes element-wise a nonlinear function of the preceding
layer's output. Historically, an activation function was considered part of
each node in each layer of the neural network. Trax follows the common current
practice of separating the activation function as its own layer, which enables
easier experimentation across different activation functions.
"""

from trax import math
from trax.layers import base
from trax.layers.base import Fn
from trax.math import numpy as np


def Relu():
  r"""Returns a layer that computes the Rectified Linear Unit (ReLU) function.

  .. math::
      f(x) = \left\{ \begin{array}{cl}
          0 & \text{if}\ x \leq 0, \\
          x & \text{otherwise}.
      \end{array} \right.
  """
  return Fn('Relu', lambda x: np.maximum(x, np.zeros_like(x)))


def ParametricRelu(a=1.):
  r"""Returns a layer that computes a ReLU function with the given slope.

  .. math::
      f(x) = \left\{ \begin{array}{cl}
          0  & \text{if}\ x \leq 0, \\
          ax & \text{otherwise}.
      \end{array} \right.

  Args:
    a: Slope of line for positive inputs.
  """
  return Fn('ParametricRelu', lambda x: np.maximum(a * x, np.zeros_like(x)))


def LeakyRelu(a=0.01):
  r"""Returns a ReLU-like layer with linear nonzero outputs for negative inputs.

  .. math::
      f(x) = \left\{ \begin{array}{cl}
          ax & \text{if}\ x \leq 0, \\
          x  & \text{otherwise}.
      \end{array} \right.

  Args:
    a: Slope of line for negative inputs.
  """
  return Fn('LeakyRelu', lambda x: np.where(x >= 0, x, a * x))


def Elu(a=1.):
  r"""Returns a ReLU-like layer with exponential outputs for negative inputs.

  .. math::
      f(x) = \left\{ \begin{array}{cl}
          a \cdot (e^x - 1) & \text{if}\ x \leq 0, \\
          x                 & \text{otherwise}.
      \end{array} \right.

  (Asymptotically, :math:`f(x)\rightarrow -a` as :math:`x\rightarrow - \infty`.)

  Args:
    a: Coefficient multiplying the exponential, for negative inputs.
  """
  return Fn('Elu', lambda x: np.where(x > 0, x, a * np.expm1(x)))


def Selu(alpha=1.6732632423543772848170429916717,
         lmbda=1.0507009873554804934193349852946):
  r"""Returns an `Elu`-like layer with an additional scaling/slope parameter.

  .. math::
      f(x) = \left\{ \begin{array}{cl}
          \lambda \cdot \alpha \cdot (e^x - 1) & \text{if}\ x \leq 0, \\
          \lambda \cdot x                      & \text{otherwise}.
      \end{array} \right.

  Args:
    alpha: Coefficient multiplying the exponential, for negative inputs.
    lmbda: Coefficient scaling the whole function.
  """
  return Fn('Selu', lambda x: lmbda * np.where(x > 0, x, alpha * np.expm1(x)))


def Gelu():
  r"""Returns a layer that computes the Gaussian Error Linear Unit function.

  .. math::
      f(x) = \frac{x}{2} \cdot (1 + \hbox{erf}(\frac{x}{\sqrt{2}}))
  """
  return Fn('Gelu', lambda x: x * 0.5 * (1.0 + math.erf(x / np.sqrt(2.0))))


def FastGelu():
  r"""Returns a layer that computes a fast approximation to `Gelu`.

  .. math::
      f(x) = \frac{x}{2} \cdot (1 + \tanh(ax + abx^3))

  where :math:`a = 0.7978845608` and :math:`b = 0.044715`.
  """
  def f(x):  # pylint: disable=invalid-name
    return 0.5 * x * (1 + np.tanh(x * 0.7978845608 * (1 + 0.044715 * x * x)))
  return Fn('FastGelu', f)


# pylint: disable=unnecessary-lambda
def Sigmoid():
  r"""Returns a layer that computes the sigmoid function.

  .. math::
      f(x) = \frac{1}{1 + e^{-x}}
  """
  return Fn('Sigmoid', lambda x: math.expit(x))


def Tanh():
  r"""Returns a layer that computes the hyperbolic tangent function.

  .. math::
      f(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}}
  """
  return Fn('Tanh', lambda x: np.tanh(x))
# pylint: enable=unnecessary-lambda


def HardSigmoid():
  r"""Returns a layer that computes a linear approximation to `Sigmoid`.

  .. math::
      f(x) = \left\{ \begin{array}{cl}
          0 & \text{if}\ x \leq 0, \\
          x & \text{if}\ 0 < x < 1, \\
          1 & \text{otherwise}.
      \end{array} \right.
  """
  return Fn('HardSigmoid', lambda x: np.maximum(0, np.minimum(1, (1 + x))))


def HardTanh():
  r"""Returns a layer that computes a linear approximation to `Tanh`.

  .. math::
      f(x) = \left\{ \begin{array}{cl}
          -1 & \text{if}\ x \leq 0, \\
          x  & \text{if}\ -1 < x < 1, \\
          1  & \text{otherwise}.
      \end{array} \right.
  """
  return Fn('HardTanh', lambda x: np.maximum(-1, np.minimum(1, x)))


def Softplus():
  r"""Returns a layer that computes the softplus function.

  .. math::
      f(x) = \ln(e^x + 1)
  """
  return Fn('Softplus', lambda x: np.logaddexp(x, 0.))


class ThresholdedLinearUnit(base.Layer):
  """Thresholded Linear Unit, c.f. https://arxiv.org/pdf/1911.09737.pdf ."""

  def init_weights_and_state(self, input_signature):
    """Initializes this layer's single weight to zero."""
    del input_signature
    self.weights = np.zeros((), dtype=np.float32)

  def forward(self, inputs):
    """Executes this layer as part of a forward pass through the model.

    Args:
      inputs: Tensor.

    Returns:
      Tensor of same shape and dtype as the input.
    """
    threshold = self.weights
    return np.maximum(inputs, threshold)
