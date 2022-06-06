# ============ Import python files ============
from hesperos.one_shot_learning.classifier import RandomForestClassifier
from hesperos.one_shot_learning.features2d import TrainingFeatures, InferingFeatures


# ============ Import python packages ============
import os
import napari
import pickle
import numpy as np


# ============ Train a classifier on the tagged pixels only ============
def rfc_training(features_df, output_classifier_path):
    """
    Train a Random Forest Classifier using the features data of labeled pixels (2 classes allowed)

    Parameters
    ----------
    features_df : dataframe
        features (normed 0-255) of all labeled pixels (0-1) of the 3D image
        as { 'LABEL'    : [0, ...., 0, 1, ....., 1],
            'Feature1' : [5, ...., 80, 255, ...., 5],
            'Feature2' : [ ... ],
                ...
            }
    output_classifier_path : str
        path file where the classifier will be saved as a .pckl file
    """

    # === Create Random Forest Classifier
    rfc = RandomForestClassifier(classifier_path='NONE', features_df=features_df)

    # === Load and equalize features data
    rfc._prepare_data_for_training()

    # === Fit the classifier using the features
    rfc.model.fit(rfc.features, rfc.labels)
    # score = rfc.model.score(rfc.features, rfc.labels)

    # === Save the classifier
    pickle.dump(rfc.model, open(output_classifier_path, 'wb'))


# ============ Infer a probability for all the pixels of a 3D image ============
def rfc_inference(features_df, output_classifier_path, proba_list, size_y, size_x):
    """
    Run a inference of a trained Random Forest Classifier on the features data given (without label data)

    Parameters
    ----------
    features_df : dataframe
        2D features (normed 0-255) of all pixels of a 2D image (so the size of the dataframe is size_x*size_y)
        as {  0 : [Feature1, Feature2, ...],
            1 : [Feature1, Feature2, ...]
                ...
            }
    output_classifier_path : str
        path file where the classifier is loaded
    proba_list : list
        description
    size_y : int
        description
    size_x : int
        description

    """

    # === Create Random Forest Classifier
    rfc = RandomForestClassifier(classifier_path=output_classifier_path, features_df=features_df)

    # === Load features data
    rfc._prepare_data_for_inference()

    # === Run inference to predict output log probabilities ===
    proba = rfc.model.predict_proba(rfc.features)
    proba = proba[:,1]
    nonzero_proba = np.array([min(max(p, 0.001), 0.999) for p in proba])
    log_proba = np.log(nonzero_proba)
    log_proba[np.where(np.isinf(log_proba))] = -100

    # === Convert it to probabilities ===
    output_proba = np.exp(log_proba)
    output_proba = output_proba * 255

    proba_list.append(output_proba.reshape(size_y, size_x).astype(np.uint8))


# ============ Run Process ============
def run_one_shot_learning(source_img, label, output_classifier_path):
    """
    Run one shot learning proccess (learning and inference)

    Parameters
    ----------
    source_img : ndarray
        3D original image
    label : ndarray
        labelled data (same size than soure_img) with 2 classes : the region of interest (1) and the "other structures" (2)
    output_classifier_path : str
        path to save the model

    Returns
    ----------
    output_proba : ndarray
        output probabilities normed between 0 to 1 (same size than source_img) where 1 is the highest probabilities for a pixel to be in the region of interest

    """

    # === Load data ===
    size_z , size_y, size_x = source_img.shape

    # === Extract tagged pixels ===
    # suppose only 2 labels
    _, label_roi, label_other = np.unique(label)

    mask_roi = (label == label_roi)
    mask_other = (label == label_other)

    # incr = round(source_img.shape[size_z]/50)

    # === Compute all features ===
    if not napari.features_3d.is_feature_computed:
        napari.features_3d._set_source_img(source_img)
        napari.features_3d._compute_features_3d()

    # === Create features data needed for training a RFC ===
    train_features = TrainingFeatures()
    for z in range(size_z):
        # Extract only features of tagged pixels
        train_features.features_2d_array = napari.features_3d.features_3d_list[z]
        train_features._extract_tagged_features(mask_roi[z, :, :], mask_other[z, :, :])

    train_features._create_features_df()

    # === Train the classifier ===
    rfc_training(train_features.features_df, output_classifier_path)
    del train_features

    # === Create 2D features data needed to infer with a RFC ===
    proba_list = []
    # for z in range(source_img.shape[0]):
    #     infer_features = InferingFeatures()
    #     infer_features._set_source_img(source_img[z, :, :])
    #     # Compute 2D features
    #     infer_features._compute_features_2d()
    #     # Create feature dataframe
    #     infer_features._create_features_df()

    for z in range(size_z):
        infer_features = InferingFeatures()
        infer_features.features_2d_array = napari.features_3d.features_3d_list[z]
        # Create feature dataframe
        infer_features._create_features_df()

    # === Infer the classifier for the corresponding 2D slice ===
        rfc_inference(infer_features.features_df, output_classifier_path, proba_list, size_y, size_x)

    # === Display the output results ===
    output_proba = np.stack(proba_list, axis=0)

    return output_proba