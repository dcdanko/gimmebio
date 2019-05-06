import tensorflow as tf
from argparse import Namespace
from gimmebio.seqtalk.deconstruction import layer_hard_softmax


def build_soft_conv_encoder(params):
    input_flat = tf.placeholder(
        tf.float32,
        [None, params.input_length * params.alphabet_size]
    )
    input_layer = tf.reshape(
        input_flat,
        [-1, params.input_length, params.alphabet_size]
    )

    def conv_layer(my_inp_layer):
        return tf.layers.conv1d(
            inputs=my_inp_layer,
            filters=params.conv_filters,
            kernel_size=params.conv_kernel_size,
            padding='same',
            activation=tf.nn.relu
        )

    conv1 = conv_layer(input_layer)
    conv2 = conv_layer(conv1)
    return input_flat, conv2


def build_dense_encoder(params):
    input_flat = tf.placeholder(
        tf.float32,
        [None, params.input_length * params.alphabet_size]
    )
    encode = tf.layers.dense(
        input_flat,
        params.dense_dims,
    )
    return input_flat, encode


def build_explicit_encoder(params, soft_encoder_out):
    return layer_hard_softmax(
        soft_encoder_out,
        [
            params.dense_dims,
            params.onehot_dims * params.explicit_neurons
        ],
        params.onehot_dims,
        temperature_tensor=params.temperature_tensor,
        stochastic_tensor=params.stochastic_tensor,
        scope="explicit",
    )


def build_projector(params, explicit, slice_inital_dim=True):
    embedding = explicit
    if slice_inital_dim:
        emb0 = tf.reshape(
            explicit, [-1, params.explicit_neurons, params.onehot_dims]
        )  # unflatten explicit neurons
        emb1 = tf.slice(
            emb0, [0, 0, 1], [-1, -1, -1]
        )  # Remove the first dimension from each explicit neuron
        embedding = tf.reshape(
            emb1, [-1, params.explicit_neurons * (params.onehot_dims - 1)]
        )  # flatten explicit neurons

    projection = tf.layers.dense(
        embedding,
        params.alphabet_size * params.input_length,
    )
    return projection


def set_loss(params, model_input, projector_out):
    autoencoder_loss = tf.reduce_mean(
        tf.reduce_sum(
            tf.square(projector_out - model_input),
            axis=1
        )
    )
    ts_autoencoder = tf.train.GradientDescentOptimizer(params.learn_rate)
    ts_autoencoder = ts_autoencoder.minimize(autoencoder_loss)
    return autoencoder_loss, ts_autoencoder


def build_explicit_autoencoder(params, encoder_type='conv'):
    """Return (input, output) layers from an explicit conv autoencoder."""
    model_input, soft_encoder_out = build_dense_encoder(params)
    explicit_encoder_out = build_explicit_encoder(params, soft_encoder_out)
    embedding = tf.reshape(explicit_encoder_out, [-1, params.explicit_neurons, params.onehot_dims])
    projector_out = build_projector(params, embedding)
    autoencoder_loss, ts_autoencoder = set_loss(
        params, model_input, projector_out
    )

    return Namespace(
        input_layer=model_input,
        learn_rate=params.learn_rate,
        stochastic=params.stochastic_tensor,
        temperature=params.temperature_tensor,
        explicit=explicit_encoder_out,
        projection=projector_out,
        autoencoder_loss=autoencoder_loss,
        ts_autoencoder=ts_autoencoder,
        init_op=tf.global_variables_initializer()
    )
