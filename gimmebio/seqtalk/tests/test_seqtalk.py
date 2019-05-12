"""Test suite for seqtalk."""

from unittest import TestCase

import tensorflow as tf
from argparse import Namespace

from gimmebio.seqtalk.autoencode.architecture import build_explicit_autoencoder
from gimmebio.seqtalk.autoencode.training import train_autoencoder
from gimmebio.seqtalk.seq_data import FastqSeqData

EXAMPLE_FASTQ = '/Users/dcdanko/Dev/gimmebio/gimmebio/sample_seqs/gimmebio/sample_seqs/data/sample_fastq_zymo_control.fq'


class TestSampleSeqs(TestCase):
    """Test suite for sample seqs."""
    '''
    def test_build_model(self):
        model = build_explicit_autoencoder(Namespace(
            onehot_dims=9,
            explicit_neurons=40,
            input_length=128,
            conv_filters=32,
            conv_kernel_size=16,
            alphabet_size=5,
            learn_rate=tf.constant(1e-1),
            temperature_tensor=tf.constant(1.0),
            stochastic_tensor=tf.constant(True),
        ))
    '''

    def test_training(self):
        model = build_explicit_autoencoder(Namespace(
            onehot_dims=9,
            explicit_neurons=40,
            dense_dims=100,
            input_length=100,
            conv_filters=32,
            conv_kernel_size=16,
            alphabet_size=4,
            learn_rate=tf.constant(1e-1),
            temperature_tensor=tf.constant(1.0),
            stochastic_tensor=tf.constant(True),
        ))
        sess = tf.InteractiveSession()
        sess.run(tf.global_variables_initializer())
        data_source = FastqSeqData(EXAMPLE_FASTQ, seq_len=100)
        tr, va = train_autoencoder(model, sess, data_source, minibatch_size=50, num_epochs=1)

