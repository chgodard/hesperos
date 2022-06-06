# ============ Import python files ============
from hesperos.one_shot_learning.features2d import Features2D


# ============ Define 3D features class ============
class Features3D:
    """
        A class used to store and compute 3D features on 3D image

    """
    def __init__(self):
        """
        Initilialisation

        """
        self.is_feature_computed = False
        self.features_3d_list = []

    def _set_source_img(self, source_img):
        """
        Define the original 3D image on which the 3D features will be calculated 

        Parameters
        ----------
        source_img : ndarray
            3D original image

        """
        self.source_img = source_img

    def _add_2d_features(self, slice_index, features_2d_array):
        """
        Add 2D features in the 3D features list

        Parameters
        ----------
        slice_index : int
            index where the 2D feature is added to the 3D features list
        features_2d_array : ndarray
            2D feature array

        """
        self.features_3d_list.insert(slice_index, features_2d_array)

    def _compute_features_3d(self):
        """
        Compute 2D features for each slice of the 3D original image

        """
        features_2d_array = None
        size_z = self.source_img.shape[0]

        for z in range(size_z):
            self._launch_3d_computation(z)

        self.is_feature_computed = True

    def _launch_3d_computation(self, ind_z):
        """
        Start computation of 2D features for one slice of the 3D original image

        Parameters
        ----------
        ind_z : int
            slice index of the 3D original image

        """
        features_2d = Features2D()
        features_2d._set_source_img(self.source_img[ind_z, :, :])

        # Compute 2D features
        features_2d_array = features_2d._compute_features_2d()
        # Save features
        self._add_2d_features(ind_z, features_2d_array)