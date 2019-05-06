import tensorflow as tf
import numpy as np

def build_feed_dict(model, epoch, batch):
    feed_dict = {model.input_layer: batch}
    if epoch < 0:  # Validation
        feed_dict[model.stochastic] = False
    elif epoch == 0:  # Warmup epoch
        feed_dict[model.learn_rate] = 1e-4
        feed_dict[model.temperature] = 3.
    elif epoch < 10:
        feed_dict[model.temperature] = 2.
    return feed_dict


def train_autoencoder(model, sess, data_source, minibatch_size=50, num_epochs=30, lr=1e-1):
    training_losses, validation_losses = [], []
    num_minibatches = len(data_source.train) // minibatch_size
    for epoch in range(num_epochs):
        epoch_loss = 0
        data_source.train.reset()
        for _ in range(num_minibatches):
            batch = data_source.train.next_batch(minibatch_size)
            batch = np.reshape(batch, [batch.shape[0], batch.shape[1] * batch.shape[2]])
            epoch_loss += sess.run(
                [model.autoencoder_loss, model.ts_autoencoder],
                feed_dict=build_feed_dict(model, epoch, batch)
            )[0]
        training_losses.append(epoch_loss / num_minibatches)

        # Run Validation
        loss = 0
        for _ in range(10):
            batch = data_source.test.next_batch(500)
            batch = np.reshape(batch, [batch.shape[0], batch.shape[1] * batch.shape[2]])
            loss += sess.run(
                [model.autoencoder_loss],
                feed_dict=build_feed_dict(model, -1, batch),
            )[0]
        validation_losses.append(loss / 10)

    return training_losses, validation_losses
