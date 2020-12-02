from pathlib import Path
from keras.models import load_model
import numpy as np
import keras
from skimage.transform import resize


def dr_dme_grade(images):
    keras.backend.clear_session()
    model = load_model("media/trained_models/dr_grading_weights.h5")
    image = np.array(images)/255.
    image = resize(image, (256, 256))
    image = np.expand_dims(image, axis=0)
    prediction = model.predict(image, steps = 1)

    return prediction


# def dme_grade(images):
#     keras.backend.clear_session()
#     model1 = load_model("media/trained_models/DME_transfer_learning.hdf5")
#     image = np.array(images)/255.
#     image = resize(image, (256, 256))
#     image = np.expand_dims(image, axis=0)
#     prediction1 = model1.predict(image, steps = 1)
#
#     return prediction1



