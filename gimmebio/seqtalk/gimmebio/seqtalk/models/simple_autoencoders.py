import torch
import torch.nn as nn
import torch.autograd.Function as F
from seqtalk.binary_neurons import StochasticBinaryActivation
from collections import namedtuple
import numpy as np

TrainingParams = namedtuple('TrainingParams', [
    'minibatch_size',
    'num_epochs',
    'minibatches_per_epoch',
    'processor',
])


def load_tensor(kind, tensor):
    if kind.lower() == 'gpu':
        return tensor.gpu()
    return tensor.cpu()


class TrainableModel(nn.Module):

    @classmethod
    def default_params(cls):
        return TrainingParams(100, 5, 1000, 'gpu')

    @classmethod
    def prep_model(cls, data_source, training_params):
        model = cls(data_source.input_length * data_source.alphabet_size)
        load_tensor(training_params.processor, model)
        model.zero_grad()
        data_source.reset()
        return model

    @classmethod
    def optimizer(cls, model, lr=None, momentum=None, sgd=True):
        if sgd:
            lr = lr if lr is not None else 0.1
            momentum = momentum if momentum is not None else 0.9
            return torch.optim.SGD(model.parameters(), lr=lr, momentum=momentum)

    @classmethod
    def loss(cls):
        return torch.nn.MSELoss(reduction='sum')

    @classmethod
    def train(cls, data_source, training_params=None):
        training_params = cls.default_params() if training_params is None else training_params
        model = cls.prep_model(data_source, training_params)
        optimizer = cls.optimizer(model)
        loss_fn = cls.loss(cls)
        for epoch in range(training_params.num_epochs):
            epoch_loss = 0
            for batch_num in range(training_params.minibatches_per_epoch):
                batch_loss = cls.train_minibatch(
                    epoch, batch_num, model,
                    optimizer, loss_fn,
                    data_source, training_params
                )
                epoch_loss += batch_loss
            yield model, (epoch, epoch_loss.cpu().data)

    @classmethod
    def train_minibatch(cls,
                        epoch_num, batch_num, model,
                        optimizer, loss_fn,
                        data_source, training_params):
        batch = data_source.next_batch(
            training_params.minibatch_size, flat=True, type=np.float64
        )
        batch = load_tensor(training_params.processor, torch.FloatTensor(batch))
        optimizer.zero_grad()
        pred = model(batch)
        loss = loss_fn(pred, batch)
        loss.backward()
        optimizer().step()
        return loss


class SimpleContinuousNet(TrainableModel):
    """A very simple network that should learn the identity matrix
    with a single layer of ReLU neurons.
    """

    def __init__(self, input_size):
        super(SimpleBinaryNet, self).__init__()

        self.fc1 = nn.Linear(input_size, input_size, bias=False)
        self.act = StochasticBinaryActivation()
        self.sig = torch.nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = x.clamp(min=0)
        x = self.sig(x)
        return x

    @classmethod
    def train_minibatch(cls,
                        epoch_num, batch_num, model,
                        optimizer, loss_fn,
                        data_source, training_params):
        batch = data_source.train.next_batch(
            training_params.minibatch_size, flat=True, type=np.float64
        )
        batch = load_tensor(training_params.processor, torch.FloatTensor(batch))
        optimizer.zero_grad()
        loss = 0
        for seq in batch:
            pred = model(seq)
            pred, seq = data_source.unflatten(pred, seq)
            pred = F.softmax(pred)
            loss += loss_fn(pred, seq)
        loss.backward()
        optimizer().step()
        return loss


class SimpleBinaryNet(TrainableModel):

    def __init__(self, input_size):
        super(SimpleBinaryNet, self).__init__()

        self.fc1 = nn.Linear(input_size, input_size, bias=False)
        self.act = StochasticBinaryActivation()
        self.sig = torch.nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.act(x)
        return x
