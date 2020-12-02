# Load the model
from tensorflow.python.keras import models
import tensorflow as tf
import tensorflow.contrib as tfcontrib
from tensorflow.python.keras import layers
from tensorflow.python.keras import losses
from tensorflow.python.keras import models
from tensorflow.python.keras import backend as K
import os
from pathlib import Path
from PIL import Image
import numpy as np


def dice_coeff(y_true, y_pred):
    smooth = 1.
    # Flatten
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    score = (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)
    return score


def dice_loss(y_true, y_pred):
    loss = 1 - dice_coeff(y_true, y_pred)
    return loss


def bce_dice_loss(y_true, y_pred):
    loss = losses.binary_crossentropy(y_true, y_pred) + dice_loss(y_true, y_pred)
    return loss


def model():
    model_path = Path('media/trained_models/SE_weights.hdf5')
    model = models.load_model(model_path, custom_objects={'bce_dice_loss': bce_dice_loss,
                                                          'dice_loss': dice_loss})

    return model


def predict_se(image):
    myModel = model()
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize_images(image, (256, 256))/255.
    image = tf.expand_dims(image, axis=0)
    predicted_image = myModel.predict(image, steps=1)
    predicted_image = np.squeeze(predicted_image, axis=0)
    predicted_image = np.squeeze(predicted_image)
    threshold = 0.9
    predicted_image = predicted_image > threshold
    predicted_mask = (predicted_image.astype('uint8'))*255
    output_image = Image.fromarray(predicted_mask)

    return output_image

