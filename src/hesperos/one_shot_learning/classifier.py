# ============ Import python packages ============
import time
import pickle
import numpy as np
import pandas as pd
import sklearn.ensemble


# ============ Define main class fr classifier ============
class Classifier():
    """
    A class used to prepare data for training and inference of a classifier

    """

    def __init__(self, classifier_path, features_df):
        """
        Initilialisation

        Parameters
        ----------
        classifier_path : str
            path file where the classifier is loaded
        features_df : dataframe
            2D features (normed 0-255) of all pixels of a 2D image (so the size of the dataframe is size_x*size_y)
            as {  0 : [Feature1, Feature2, ...],
                1 : [Feature1, Feature2, ...]
                    ...
                }

        """
        self.classifier_path = classifier_path
        self.features_df = features_df

        self.labels = None
        self.features = None

    def _prepare_data_for_training(self):
        """
        Modify the features dataframe to correspond to the requirement of the "rfc_training" function:

            features (normed 0-255) of all labeled pixels (0-1) of the 3D image
            as { 'LABEL'    : [0, ...., 0, 1, ....., 1],
                'Feature1' : [5, ...., 80, 255, ...., 5],
                'Feature2' : [ ... ],
                    ...
                }

        """
        # Separate states (i.e. label tags -- 0 or 1) from features
        df_0 = self.features_df[ self.features_df.iloc[:,0] == 0 ]
        df_1 = self.features_df[ self.features_df.iloc[:,0] == 1 ]

        nb_size_df = self.features_df.shape
        nb_size_df_0 = df_0.shape
        nb_size_df_1 = df_1.shape

        nb_to_gen = int(nb_size_df[0])
        nb_to_gen_2 = int(np.floor(nb_to_gen/2))
        nb_to_gen_0 = int(nb_size_df_0[0])
        nb_to_gen_1 = int(nb_size_df_1[0])

        II_0 = np.random.randint(nb_to_gen_0, size =nb_to_gen_2)
        II_1 = np.random.randint(nb_to_gen_1, size =nb_to_gen_2)

        df_0 = df_0.iloc[II_0]
        df_1 = df_1.iloc[II_1]
        df = pd.concat([df_0,df_1])

        # split dataframe
        temp_labels = df.iloc[:,0].copy()
        temp_features = df.drop(df.columns[0],axis = 1) # remove labels column

        # dataframe to array
        labels = temp_labels.values
        self.labels = np.ravel(labels)
        self.features = temp_features.values

    def _prepare_data_for_inference(self):
        """
        Extract the dataframe, all ready in the good format for the "rfc_inference" function

        """
        self.features = self.features_df


# ============ Define inherent class for Random Forest ============
class RandomForestClassifier(Classifier):
    """
    A class used to create a Random Forest Classfier and prepare data for training and inference

    """
    def __init__(self, classifier_path, features_df):
        """
        Initilialisation

        Parameters
        ----------
        classifier_path : str
            path file where the classifier is loaded
        features_df : dataframe
            2D features (normed 0-255) of all pixels of a 2D image (so the size of the dataframe is size_x*size_y)
            as {  0 : [Feature1, Feature2, ...],
                1 : [Feature1, Feature2, ...]
                    ...
                }

        """
        Classifier.__init__(self, classifier_path, features_df)

        self.nb_tree      = 50
        self.max_depth    = 50

        self.criterion    = 'gini'
        self.max_features = "sqrt"

        self.oob_score    = True
        self.warm_start   = False
        self.bootstrap    = True
        self.class_weight = None

        try :
            self.model = pickle.load(open(self.classifier_path, 'rb'))
        except:
            self.model = sklearn.ensemble.RandomForestClassifier(n_estimators=self.nb_tree, max_depth=self.max_depth, criterion=self.criterion, max_features=self.max_features, oob_score=self.oob_score, warm_start=self.warm_start, bootstrap=self.bootstrap, class_weight=self.class_weight)