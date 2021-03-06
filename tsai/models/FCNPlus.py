# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/103c_models.FCNPlus.ipynb (unless otherwise specified).

__all__ = ['FCNPlus']

# Cell
from ..imports import *
from .layers import *

# Cell
class FCNPlus(Module):
    def __init__(self, c_in, c_out, layers=[128, 256, 128], kss=[7, 5, 3], coord=False, separable=False,
                 zero_norm=False, act=nn.ReLU, act_kwargs={}, residual=False):
        assert len(layers) == len(kss)
        self.residual = residual
        self.convblock1 = ConvBlock(c_in, layers[0], kss[0], coord=coord, separable=separable, act=act, act_kwargs=act_kwargs)
        self.convblock2 = ConvBlock(layers[0], layers[1], kss[1], coord=coord, separable=separable, act=act, act_kwargs=act_kwargs)
        self.convblock3 = ConvBlock(layers[1], layers[2], kss[2], coord=coord, separable=separable, zero_norm=zero_norm if residual else False,
                                    act=None if residual else act, act_kwargs=act_kwargs)
        if residual: self.shortcut = BN1(layers[2]) if c_in == layers[2] else ConvBlock(c_in, layers[2], 1, coord=coord, act=None)
        self.add = Add() if residual else noop
        self.gap = nn.AdaptiveAvgPool1d(1)
        self.squeeze = Squeeze(-1)
        self.fc = nn.Linear(layers[-1], c_out)

    def forward(self, x):
        if self.residual: res = x
        x = self.convblock1(x)
        x = self.convblock2(x)
        x = self.convblock3(x)
        if self.residual: x = self.add(x, self.shortcut(res))
        x = self.squeeze(self.gap(x))
        return self.fc(x)