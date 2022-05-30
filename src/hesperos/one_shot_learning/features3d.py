# ============ Import python files ============
from hesperos.one_shot_learning.features2d import Features2D


# ============ Define Class ============
class Features3D:
    """
        Description

    """
    def __init__(self):
        """
        Description

        """

        self.is_feature_computed = False
        self.features_3d_list = []

    def _set_source_img(self, source_img):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        self.source_img = source_img

    def _add_2d_features(self, slice_index, features_2d_array):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        self.features_3d_list.insert(slice_index, features_2d_array)

    def _compute_features_3d(self):
        """
        Description

        """

        # === Compute 2D features for each slice ===

        features_2d_array = None
        # tiff
        size_z = self.source_img.shape[0]
        # DICOM
        # size_z = self.source_img.shape[2]

        # print(f'starting computations on {multiprocessing.cpu_count()} cores')

        # TESTS MULTIPOOLING
        # pool = multiprocessing.Pool()

        # with multiprocessing.Pool() as pool:
        #     b = pool.map(self._launch_3d_computation, iterable=iter(range(size_z)))
        #     print(b)
        # pool.map_async(self._launch_3d_computation, iterable=iter(range(size_z)))

        # pool.starmap(self._launch_3d_computation, iterable=iter(range(size_z)))
        # pool.imap(self._launch_3d_computation, iterable=range(size_z), chunksize=5)
        # pool.close()

        # b = pool.map(self._launch_3d_computation, iterable=iter(range(size_z)))
        # print(b)
        # pool.start()
        # pool.join() # problem : open new app windows


        for z in range(size_z):
            self._launch_3d_computation(z)

        self.is_feature_computed = True

    def _launch_3d_computation(self, ind_z):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """

        features_2d = Features2D()
        #tiff
        features_2d._set_source_img(self.source_img[ind_z, :, :])
        # DICOM
        # features_2d._set_source_img()
        # Compute 2D features
        features_2d_array = features_2d._compute_features_2d()
        # Save features
        self._add_2d_features(ind_z, features_2d_array)