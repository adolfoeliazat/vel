import hashlib
import torch.nn as nn

import vel.util.module_util as mu

from vel.metrics.loss_metric import Loss
from vel.util.summary import summary


class Model(nn.Module):
    """ Class representing full neural network model """

    def metrics(self) -> list:
        """ Set of metrics for this model """
        return [Loss()]

    def train(self, mode=True):
        r"""
        Sets the module in training mode.

        This has any effect only on certain modules. See documentations of
        particular modules for details of their behaviors in training/evaluation
        mode, if they are affected, e.g. :class:`Dropout`, :class:`BatchNorm`,
        etc.

        Returns:
            Module: self
        """
        super().train(mode)

        if mode:
            mu.apply_leaf(self, mu.set_train_mode)

        return self

    def summary(self, input_size=None, hashsummary=False):
        """ Print a model summary """

        if input_size is None:
            print(self)
            print("-" * 120)
            number = sum(p.numel() for p in self.model.parameters())
            print("Number of model parameters: {:,}".format(number))
            print("-" * 120)
        else:
            summary(self, input_size)

        if hashsummary:
            for idx, hashvalue in enumerate(self.hashsummary()):
                print(f"{idx}: {hashvalue}")

    def hashsummary(self):
        """ Print a model summary - checksums of each layer parameters """
        children = list(self.children())

        result = []

        for child in children:
            result.extend(hashlib.sha256(x.detach().cpu().numpy().tobytes()).hexdigest() for x in child.parameters())

        return result

    def get_layer_groups(self):
        """ Return layers grouped """
        return [self]

    def reset_weights(self):
        """ Call proper initializers for the weights """
        pass


class BackboneModel(Model):
    """ Model that serves as a backbone network to connect your heads to """


class LinearBackboneModel(BackboneModel):
    """ Model that serves as a backbone network to connect your heads to - one that spits a single-dimension output """

    @property
    def output_dim(self):
        """ Final dimension of model output """
        raise NotImplementedError


class SupervisedModel(Model):
    """ Model for a supervised learning probvlem"""
    def loss(self, x_data, y_true):
        """ Forward propagate network and return a value of loss function """
        y_pred = self(x_data)
        return y_pred, self.loss_value(x_data, y_true, y_pred)

    def loss_value(self, x_data, y_true, y_pred):
        """ Calculate a value of loss function """
        raise NotImplementedError
