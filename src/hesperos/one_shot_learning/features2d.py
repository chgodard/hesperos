# ============ Import python packages ============
import numpy as np
import pandas as pd
import scipy.ndimage as ndim
from skimage.morphology import disk
from skimage.filters.rank import entropy
from scipy.ndimage.morphology import distance_transform_cdt


# ============ Import python files ============
from hesperos.one_shot_learning.kernel import gaussian_kernel_3x3, gaussian_kernel_5x5, prewitt_kernel_3x3, prewitt_kernel_5x5, laplacian_kernel_3x3, laplacian_kernel_5x5


# ============ Utilities function ============
def norm(source_img):
    """  Normalize an array to 0-1

	Parameters
    ----------
	source_img : ndarray
		raw image

    Returns
    ----------
    out : ndarray (float)
        normed image

    """
    return ((source_img - source_img.min())/(source_img.max() - source_img.min()))


# ============ Define fetaures Class ============
class Features2D:
    """
        Description

    """
    def __init__(self):
        """
        Description

        """
        self.feature_to_compute = {'entropy', 'gaussian_blur', 'gradient', 'maximum', 'mean', 'sdf', 'minimum', 'laplacian', 'stddev'}
        self.feature_list = []
        self.features_2d_array = None

        self.source_img = None
        self.norm_img = None

    def _set_source_img(self, source_img):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        self.source_img = source_img
        self.norm_img = norm(source_img) * 255
        # Add pixel value as feature
        self.feature_list.append(source_img)

    def _compute_features_2d(self):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        Returns:
        --------
        output : type
            description

        """
        for f in self.feature_to_compute:
            if f == 'entropy':
                self._calculate_entropy(radius=1)
                self._calculate_entropy(radius=3)

            elif f == 'stddev':
                self._calculate_stddev(radius=1)
                self._calculate_stddev(radius=5)

            elif f == 'gaussian_blur':
                self._calculate_gaussian_blur(gaussian_kernel_3x3)
                self._calculate_gaussian_blur(gaussian_kernel_5x5)

            elif f == 'gradient':
                self._calculate_gradient(prewitt_kernel_3x3, kernel_size=3)
                self._calculate_gradient(prewitt_kernel_5x5, kernel_size=5)

            elif f == 'laplacian':
                self._calculate_laplacian(laplacian_kernel_3x3, scaling=2)
                self._calculate_laplacian(laplacian_kernel_5x5, scaling=32)

            elif f == 'maximum':
                self._calculate_maximum(radius=1)
                self._calculate_maximum(radius=5)
                self._calculate_maximum(radius=9)

            elif f == 'minimum':
                self._calculate_minimum(radius=1)
                self._calculate_minimum(radius=5)
                self._calculate_minimum(radius=9)

            elif f == 'mean':
                self._calculate_mean(radius=1)
                self._calculate_mean(radius=5)

            elif f == 'sdf':
                self._calculate_sdf()

        return np.stack(self.feature_list)
        # self.features_2d_array = np.stack(self.feature_list)
        # self.feature_list = []

    def _calculate_entropy(self, radius):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        img_div = self.norm_img / 32
        value = entropy(img_div.astype(np.uint8), disk(radius))
        feature = np.minimum(value * 64, np.ones(img_div.shape) * 255)
        self.feature_list.append(norm(feature))

    def _calculate_stddev(self, radius):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        mean = ndim.convolve(self.norm_img, disk(radius)) / disk(radius).sum()
        diff = self.norm_img - mean
        diff[diff < 0] = 0
        res = ndim.convolve(diff * diff, disk(radius))
        feature = np.sqrt(res / (disk(radius).sum() - 1))
        self.feature_list.append(norm(feature))

    def _calculate_gaussian_blur(self, kernel):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        feature = ndim.convolve(self.norm_img, kernel) / kernel.sum()
        self.feature_list.append(norm(feature))

    def _calculate_laplacian(self, kernel, scaling):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        feature = ndim.convolve(self.norm_img, kernel) / scaling + 127
        self.feature_list.append(norm(feature))

    def _calculate_gradient(self, kernel, kernel_size):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        gx = ndim.convolve(self.norm_img, kernel) / (kernel_size * kernel_size)
        gy = ndim.convolve(self.norm_img, kernel.transpose((1,0))) / (kernel_size * kernel_size)
        feature = np.sqrt(gx * gx + gy * gy)
        self.feature_list.append(norm(feature))

    def _calculate_maximum(self, radius):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        feature = ndim.maximum_filter(self.norm_img, footprint=disk(radius))
        self.feature_list.append(norm(feature))

    def _calculate_minimum(self, radius):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        feature = ndim.minimum_filter(self.norm_img, footprint=disk(radius))
        self.feature_list.append(norm(feature))

    def _calculate_mean(self, radius):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description

        """
        feature = ndim.convolve(self.norm_img, disk(radius)) / disk(radius).sum()
        self.feature_list.append(norm(feature))

    def _calculate_sdf(self):
        """
        Description

        """

        # define intervals of pixel intensity to keep for successive sdf calculation
        bornes = [[0,120], [60,180], [120,255], [20,100], [50,130], [80,160], [110,190], [140,220], [170,255], [40,80], [100,140], [160,200]]

        feature_list = []
        # iterate over pixel intensity intervals

        for b in bornes:
            # keep all pixels with intensity ranging in the given interval
            inf_img = self.source_img > b[0]
            sup_img = self.source_img < b[1]
            input_img = inf_img & sup_img

            # calculate signed distance fields
            self.feature_list.append(distance_transform_cdt(input_img))


# ============ Define fetaures Class ============
class TrainingFeatures(Features2D):
    """
        Description

    """
    def __init__(self):
        """
        Description

        """
        Features2D.__init__(self)
        self.feature_list_roi = None
        self.feature_list_other = None
        self.features_df = pd.DataFrame()

    def _extract_tagged_features(self, mask_roi, mask_other):
        """
        Description

        Parameters
        ----------
        param_1 : type
            description


        """
        nb_features = self.features_2d_array.shape[0]

        if self.feature_list_roi is None : self.feature_list_roi = [ [] for _ in range(nb_features) ]
        if self.feature_list_other is None : self.feature_list_other = [ [] for _ in range(nb_features) ]

        for f in range(nb_features):
            self.feature_list_roi[f].extend(np.extract(mask_roi, self.features_2d_array[f,:,:]))
            self.feature_list_other[f].extend(np.extract(mask_other, self.features_2d_array[f,:,:]))

    def _create_features_df(self):
        """
        Description

        """
        roi_features_df = pd.DataFrame([1] * len(self.feature_list_roi[8]), columns=['LABEL'])
        other_features_df = pd.DataFrame([0] * len(self.feature_list_other[8]), columns=['LABEL'])

        nb_features = self.features_2d_array.shape[0]
        for f in range(nb_features):
            roi_features_df['FEATURE {0}'.format(f)] = self.feature_list_roi[f]
            other_features_df['FEATURE {0}'.format(f)] = self.feature_list_other[f]

        self.features_df = pd.concat((roi_features_df, other_features_df), axis=0)


class InferingFeatures(Features2D):
    """
        Description

    """
    def __init__(self):
        """
        Description

        """
        Features2D.__init__(self)
        self.features_df = pd.DataFrame()

    def _create_features_df(self):
        """
        Description

        """
        self.features_df = pd.concat((self.features_df, pd.DataFrame(np.transpose(self.features_2d_array.reshape(self.features_2d_array.shape[0], -1)))), axis=1)