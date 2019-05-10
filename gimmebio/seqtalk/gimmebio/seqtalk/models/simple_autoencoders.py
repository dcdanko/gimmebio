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


class SimpleContinuousNet(nn.Module):
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
    def prep_model(cls, data_source, training_params):
        model = cls(data_source.input_length * data_source.alphabet_size)
        load_tensor(training_params.processor, model)
        model.zero_grad()
        data_source.train.reset()
        return model

    @classmethod
    def train(cls, data_source, training_params):
        model = cls.prep_model(data_source, training_params)

        loss_fn = torch.nn.MSELoss(reduction='sum')
        optimizer = torch.optim.SGD(model.parameters(), lr=0.5, momentum=0.9)
        for epoch in range(training_params.num_epochs):
            epoch_loss = 0
            for _ in range(training_params.minibatches_per_epoch):
                batch = data_source.train.next_batch(
                    training_params.minibatch_size, flat=True, type=np.float64
                )
                batch = load_tensor(training_params.processor, torch.FloatTensor(batch))
                loss = 0
                for seq in batch:
                    model.zero_grad()
                    pred = model(seq)
                    pred, seq = data_source.unflatten(pred, seq)
                    pred = F.softmax(pred)
                    loss += loss_fn(pred, seq)
                    epoch_loss += loss
                loss.backward()
                optimizer.step()
            yield model, (epoch, epoch_loss.cpu().data)


class SimpleBinaryNet(nn.Module):

    def __init__(self, input_size):
        super(SimpleBinaryNet, self).__init__()

        self.fc1 = nn.Linear(input_size, input_size, bias=False)
        self.act = StochasticBinaryActivation()
        self.sig = torch.nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        #x = x.clamp(min=0)
        x = self.act(x)
        return x