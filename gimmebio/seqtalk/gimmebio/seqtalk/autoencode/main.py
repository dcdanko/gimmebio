import click
import tensorflow as tf
from argparse import Namespace
from .architecture import build_explicit_autoencoder
from .training import train_autoencoder
from seqtalk.data_source import FastqSeqData


@click.group()
def main():
    pass


@main.command('train')
@click.option('--num-reads', default=10 * 1000 * 1000)
@click.option('--minibatch-size', default=50)
@click.option('--num-epochs', default=30)
@click.argument('fastq_file')
def train_new(fastq_file):
    model = build_explicit_autoencoder(Namespace(
        onehot_dims=9,
        explicit_neurons=40,
        input_length=128,
        conv_filters=16,
        conv_kernel_size=16,
        alphabet_size=5,
        learn_rate=tf.constant(1e-1),
        temperature_tensor=tf.constant(1.0),
        stochastic_tensor=tf.constant(True),
    ))
    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())
    data_source = FastqSeqData(fastq_file)
    tr, va = train_autoencoder(model, sess, data_source, num_epochs=30)


if __name__ == '__main__':
    main()
