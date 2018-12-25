import tensorflow as tf, numpy as np, matplotlib.pyplot as plt, matplotlib.cm as cm
from tensorflow.python.framework import ops
from mpl_toolkits.axes_grid1 import ImageGrid
from tensorflow.examples.tutorials.mnist import input_data
import bisect, math
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

def plot_nxn(n, images):
    """Plots nxn MNIST images"""
    images = images.reshape((n*n,28,28))
    fig = plt.figure(1, (n, n))
    grid = ImageGrid(fig, 111,  # similar to subplot(111)
                     nrows_ncols=(n, n),  # creates grid of axes
                     axes_pad=0.1,  # pad between axes in inch.
                     share_all=True,
                     )

    grid.axes_llc.set_xticks([])
    grid.axes_llc.set_yticks([])

    for i in range(n*n):
        grid[i].imshow(images[i], cmap = cm.Greys_r)  # The AxesGrid object work as a list of axes.

    plt.show()

def plot_2xn(n, images):
    """Plots 2xn MNIST images"""
    images = images.reshape((2*n,28,28))
    fig = plt.figure(1, (n, 2))
    grid = ImageGrid(fig, 111,  # similar to subplot(111)
                     nrows_ncols=(2, n),  # creates grid of axes
                     axes_pad=0.1,  # pad between axes in inch.
                     share_all=True,
                     )

    grid.axes_llc.set_xticks([])
    grid.axes_llc.set_yticks([])

    for i in range(2*n):
        grid[i].imshow(images[i], cmap = cm.Greys_r)  # The AxesGrid object work as a list of axes.

    plt.show()

def plot_mxn(m, n, images):
    """Plots 2xn MNIST images"""
    images = images.reshape((m*n,28,28))
    fig = plt.figure(1, (n, m))
    grid = ImageGrid(fig, 111,  # similar to subplot(111)
                     nrows_ncols=(m, n),  # creates grid of axes
                     axes_pad=0.1,  # pad between axes in inch.
                     share_all=True,
                     )

    grid.axes_llc.set_xticks([])
    grid.axes_llc.set_yticks([])

    for i in range(m*n):
        grid[i].imshow(images[i], cmap = cm.Greys_r)  # The AxesGrid object work as a list of axes.

    plt.show()

def plot_n(data_and_labels, lower_y = 0., title="Learning Curves"):
    fig, ax = plt.subplots()
    for data, label in data_and_labels:
        ax.plot(range(0,len(data)*100,100),data, label=label)
    ax.set_xlabel('Training steps')
    ax.set_ylabel('Accuracy')
    ax.set_ylim([lower_y,1])
    ax.set_title(title)
    ax.legend(loc=4)
    plt.show()

def reset_graph():
    if 'sess' in globals() and sess:
        sess.close()
    tf.reset_default_graph()

def layer_linear(inputs, shape, scope='linear_layer'):
    with tf.variable_scope(scope):
        w = tf.get_variable('w',shape)
        b = tf.get_variable('b',shape[-1:])
    return tf.matmul(inputs,w) + b

def layer_conv(inputs, filter_width, input_channels, output_channels, scope='conv_layer'):
    with tf.variable_scope(scope):
        w = tf.get_variable('w',[filter_width, filter_width, input_channels, output_channels])
        b = tf.get_variable('b',[output_channels])
    return tf.nn.relu(tf.nn.conv2d(inputs, w, strides=[1, 1, 1, 1], padding='SAME')) + b

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')

def layer_softmax(inputs, shape, scope='softmax_layer'):
    with tf.variable_scope(scope):
        w = tf.get_variable('w',shape)
        b = tf.get_variable('b',shape[-1:])
    return tf.nn.softmax(tf.matmul(inputs,w) + b)

def compute_accuracy(y, pred):
    correct = tf.equal(tf.argmax(y,1), tf.argmax(pred,1))
    return tf.reduce_mean(tf.cast(correct, tf.float32))

def st_sampled_softmax(logits):
    """Takes logits and samples a one-hot vector according to them, using the straight
    through estimator on the backward pass."""
    with ops.name_scope("STSampledSoftmax") as name:
        probs = tf.nn.softmax(logits)
        onehot_dims = logits.get_shape().as_list()[1]
        res = tf.one_hot(tf.squeeze(tf.multinomial(logits, 1), 1), onehot_dims, 1.0, 0.0)
        with tf.get_default_graph().gradient_override_map({'Ceil': 'Identity', 'Mul': 'STMul'}):
            return tf.ceil(res*probs)

def st_hardmax_softmax(logits):
    """Takes logits and creates a one-hot vector with a 1 in the position of the maximum
    logit, using the straight through estimator on the backward pass."""
    with ops.name_scope("STHardmaxSoftmax") as name:
        probs = tf.nn.softmax(logits)
        onehot_dims = logits.get_shape().as_list()[1]
        res = tf.one_hot(tf.argmax(probs, 1), onehot_dims, 1.0, 0.0)
        with tf.get_default_graph().gradient_override_map({'Ceil': 'Identity', 'Mul': 'STMul'}):
            return tf.ceil(res*probs)

@ops.RegisterGradient("STMul")
def st_mul(op, grad):
    """Straight-through replacement for Mul gradient (does not support broadcasting)."""
    return [grad, grad]

def layer_hard_softmax(x, shape, onehot_dims, temperature_tensor=None, stochastic_tensor=None,
                       scope='hard_softmax_layer'):
    """
    Creates a layer of one-hot neurons. Note that the neurons are flattened before returning,
    so that the shape of the layer needs to be a multiple of the dimension of the one-hot outputs.

    Arguments:
    * x: the layer inputs / previous layer
    * shape: the tuple of [size_previous, layer_size]. Layer_size must be a multiple of onehot_dims,
        since each neuron's output is flattened (i.e., the number of neurons will only be
        layer_size / onehot_dims)
    * onehot_dims: the size of each neuron's output
    * temperature_tensor: the temperature for the softmax
    * stochastic_tensor: whether the one hot outputs are sampled from the softmax distribution
        (stochastic - recommended for training), or chosen according to its maximal element
        (deterministic - recommended for inference)
    """
    assert(len(shape) == 2)
    assert(shape[1] % onehot_dims == 0)
    if temperature_tensor is None:
        temperature_tensor = tf.constant(1.)
    if stochastic_tensor is None:
        stochastic_tensor = tf.constant(True)

    with tf.variable_scope(scope):
        w = tf.get_variable('w',shape)
        b = tf.get_variable('b',shape[-1:])
    logits = tf.reshape((tf.matmul(x, w) + b) / temperature_tensor,
                        [-1, onehot_dims])

    return tf.cond(stochastic_tensor,
                lambda: tf.reshape(st_sampled_softmax(logits), [-1, shape[1]]),
                lambda: tf.reshape(st_hardmax_softmax(logits), [-1, shape[1]]))

def build_classifier(onehot_dims = 8, explicit_neurons = 80, real_neurons = 0):
    reset_graph()

    x = tf.placeholder(tf.float32, [None, 784], name='x_placeholder')
    y = tf.placeholder(tf.float32, [None, 10], name='y_placeholder')
    stochastic_tensor = tf.constant(True)
    temperature_tensor = tf.constant(1.0)
    dropout = tf.placeholder_with_default(1., [])
    lr = tf.constant(1e-1)

    x_img = tf.reshape(x, [-1, 28, 28, 1])

    conv1 = layer_conv(x_img, 5, 1, 16, scope="conv1")
    mp1 = max_pool_2x2(conv1)

    mp1_flat = tf.reshape(mp1, [-1, 14*14*16])

    real = tf.sigmoid(layer_linear(mp1_flat, [14*14*16, real_neurons], scope="real"))
    explicit = layer_hard_softmax(mp1_flat, [14*14*16, onehot_dims * explicit_neurons],
                    onehot_dims, temperature_tensor, stochastic_tensor, scope="explicit")

    embedding = tf.reshape(explicit, [-1, explicit_neurons, onehot_dims])

    emb0 = tf.slice(embedding, [0,0,1], [-1, -1, -1])
    emb1 = tf.reshape(emb0, [-1, explicit_neurons * (onehot_dims-1)])

    if not real_neurons:
        emb2 = emb1
    elif explicit_neurons:
        emb2 = tf.concat(1, [real, emb1])
    else:
        emb2 = real

    projection = tf.sigmoid(layer_linear(emb2, [(onehot_dims-1) * explicit_neurons + real_neurons, 784]))

    preds = layer_softmax(tf.nn.dropout(emb2, dropout), [(onehot_dims-1) * explicit_neurons + real_neurons, 10])

    loss_classification = tf.reduce_mean(-tf.reduce_sum(y * tf.log(preds), axis=1))
    loss_autoencoder = tf.reduce_mean(tf.reduce_sum(tf.square(projection - x), axis=1))

    ts_classification = tf.train.GradientDescentOptimizer(lr).minimize(loss_classification)
    ts_autoencoder    = tf.train.GradientDescentOptimizer(lr).minimize(loss_autoencoder)

    accuracy = compute_accuracy(y, preds)

    return dict(
        x=x,
        y=y,
        lr=lr,
        dropout=dropout,
        stochastic=stochastic_tensor,
        temperature=temperature_tensor,
        real=real,
        explicit=explicit,
        embedding=embedding,
        projection=projection,
        loss_classification=loss_classification,
        loss_autoencoder=loss_autoencoder,
        ts_classification=ts_classification,
        ts_autoencoder=ts_autoencoder,
        accuracy=accuracy,
        init_op=tf.global_variables_initializer()
    )

# We are using this to make it so that the first dimension of each neuron is dead / silent
def gen_zero_batch(n):
    emb = np.zeros((n, 80, 8))
    emb[:, :, 0] = 1
    return np.zeros((n, 784)), emb

def train_autoencoder(g, sess, num_epochs=30, use_zero_batches=True, lr=1e-1):
    tr_losses, val_losses = [], []
    for epoch in range(num_epochs):
        # Run Training
        loss = 0
        for i in range(1100):
            X, _ = mnist.train.next_batch(50)
            feed_dict={g['x']: X}
            if epoch == 0: # Warmup epoch
                feed_dict[g['lr']] = 1e-4
                feed_dict[g['temperature']] = 3.
            elif epoch < 10:
                feed_dict[g['temperature']] = 2.
            l, _ = sess.run([g['loss_autoencoder'], g['ts_autoencoder']], feed_dict = feed_dict)
            loss += l
            if use_zero_batches:
                X, emb = gen_zero_batch(1)
                feed_dict={g['x']: X, g['embedding']: emb, g['lr']: lr}
                sess.run(g['ts_autoencoder'], feed_dict=feed_dict)
        tr_losses.append(loss / 1100)

        # Run Validation
        loss = 0
        for i in range(10):
            X, _ = mnist.validation.next_batch(500)
            feed_dict={g['x']: X, g['stochastic']: False}
            l, = sess.run([g['loss_autoencoder']], feed_dict = feed_dict)
            loss += l
        val_losses.append(loss / 10)

        # Report Results
        print('Epoch {:d} training/validation loss: {:0.4f}/{:0.4f}'.format(epoch+1,tr_losses[-1],val_losses[-1]))
    return tr_losses, val_losses

def eval_accuracy(g, sess, mnist_set):
    acc = 0
    for i in range(len(mnist_set.labels) // 1000):
        X, Y = mnist_set.images[i*1000:(i+1)*1000], mnist_set.labels[i*1000:(i+1)*1000]
        feed_dict={g['x']: X, g['y']: Y}
        acc_, = sess.run([g['accuracy']], feed_dict = feed_dict)
        acc += acc_
    print('Accuracy: {:0.4f}'.format(acc/(len(mnist_set.labels) // 1000)))
    return acc/(len(mnist_set.labels) // 1000)

def train_classifier(g, mnist, lr=1e-1, dropout=0.7):
    tr_losses, val_losses = [], []
    for epoch in range(20):
        acc = 0
        for i in range(1100):
            X, Y = mnist.train.next_batch(50)
            feed_dict={g['x']: X, g['y']: Y, g['dropout']: dropout}
            acc_, _ = sess.run([g['accuracy'], g['ts_classification']], feed_dict = feed_dict)
            acc += acc_
        tr_losses.append(acc / 1100)

        # Run Validation
        print("Val {} ".format(epoch), end="")
        val_losses.append(eval_accuracy(mnist.validation))

        # Report Results
        print('Epoch {:d} training loss: {:0.4f}'.format(epoch+1,tr_losses[-1]))
    return tr_losses, val_losses

def build_recurrent_generator(state_size = 1000):
    with tf.name_scope('generator'), tf.variable_scope('generator'):
        x = tf.placeholder(tf.int32, [None, None], name='x_placeholder') # [batch_size, num_steps]
        y = tf.placeholder(tf.int32, [None, None], name='y_placeholder')
        lr = tf.constant(2e-3)

        batch_size = tf.shape(x)[0]

        x_one_hot = tf.one_hot(tf.reshape(x, [-1]), 640, 1., 0.)
        rnn_inputs = tf.reshape(layer_linear(x_one_hot, [640, 100]), [batch_size, -1, 100])

        cell = tf.nn.rnn_cell.GRUCell(state_size)
        init_state = cell.zero_state(batch_size, tf.float32)
        rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, rnn_inputs, initial_state=init_state)

        flat_outputs = tf.reshape(rnn_outputs, [-1, state_size])

        with tf.variable_scope('layer_linear'):
            w = tf.get_variable('w',[state_size, 640])
            b = tf.get_variable('b',[640])

        flat_logits = tf.matmul(flat_outputs, w) + b
        flat_y = tf.reshape(y, [-1])

        next_y_dist = tf.nn.softmax(tf.matmul(final_state, w) + b)

        loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(flat_logits, flat_y))

        opt = tf.train.AdamOptimizer(lr)
        variables = [v for v in tf.global_variables() if 'generator' in v.name]
        grads = tf.gradients(loss, variables)
        grads, _ = tf.clip_by_global_norm(grads, 1.0)
        gvs = zip(grads, variables)

        ts = opt.apply_gradients(gvs)

        return dict(
            x=x,
            y=y,
            lr=lr,
            init_state=init_state,
            final_state=final_state,
            loss=loss,
            ts=ts,
            next_y_dist=next_y_dist,
            init_op=tf.global_variables_initializer()
        )

def train_RNN(h, sess, batch_generator, epochs=20):
    tr_losses = []
    for epoch in range(epochs):
        # Run training
        loss = 0
        for minibatch in range(1100):
            x, y = batch_generator(50)
            feed_dict={h['x']: x, h['y']: y}
            l, _ = sess.run([h['loss'], h['ts']], feed_dict = feed_dict)
            loss += l
        tr_losses.append(loss / 1100)

        # Report Results
        print('Epoch {:d} training loss: {:0.4f}'.format(epoch+1,tr_losses[-1]))

def intersect_sorted(a1, a2):
  """Yields the intersection of sorted lists a1 and a2, without deduplication.

  Execution time is O(min(lo + hi, lo * log(hi))), where lo == min(len(a1),
  len(a2)) and hi == max(len(a1), len(a2)). It can be faster depending on
  the data.

  # TAKEN FROM: http://ptspts.blogspot.com/2015/11/how-to-compute-intersection-of-two.html
  """
  s1, s2 = len(a1), len(a2)
  i1 = i2 = 0
  if s1 and s1 + s2 > min(s1, s2) * math.log(max(s1, s2)) * 1.4426950408889634:
    bi = bisect.bisect_left
    while i1 < s1 and i2 < s2:
      v1, v2 = a1[i1], a2[i2]
      if v1 == v2:
        yield v1
        i1 += 1
        i2 += 1
      elif v1 < v2:
        i1 = bi(a1, v2, i1)
      else:
        i2 = bi(a2, v1, i2)
  else:  # The linear solution is faster.
    while i1 < s1 and i2 < s2:
      v1, v2 = a1[i1], a2[i2]
      if v1 == v2:
        yield v1
        i1 += 1
        i2 += 1
      elif v1 < v2:
        i1 += 1
      else:
        i2 += 1

def union_sorted(a1, a2):
    return sorted(set(a1+a2))
