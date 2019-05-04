import numpy as np
import skimage.transform
import skimage.filters
import itertools
from scipy import ndimage as ndi
from collections.abc import Iterable
from skimage import util

# Parameters
p = 3
q = 10
k = .25
R = .5
e = 2.718281828


# Slight modification of preexisting algorithm used for Niblack and Sauvola Thresholding, based of the scipy
# implementation. The real trick is using their version of _mean_std which efficiently computes the mean, std for
# each pixel group (sliding window). These values are then plugged into phansalkers equation and compared to the original
def pfilter(img):
    og_img = np.array(img)/255  # Normalize the images
    m, s = _mean_std(og_img, 3)
    return og_img > m * (1 + (p * (e ** (-q * m))) + (k * ((s / R) - 1)))


# Exact code as found in the filters package of scipy with the exception of removing the line related to valid window
# sizes, as I am not going to let the user specify window size.
def _mean_std(image, w):
    """Return local mean and standard deviation of each pixel using a
    neighborhood defined by a rectangular window size ``w``.
    The algorithm uses integral images to speedup computation. This is
    used by :func:`threshold_niblack` and :func:`threshold_sauvola`.
    Parameters
    ----------
    image : ndarray
        Input image.
    w : int, or iterable of int
        Window size specified as a single odd integer (3, 5, 7, …),
        or an iterable of length ``image.ndim`` containing only odd
        integers (e.g. ``(1, 5, 5)``).
    Returns
    -------
    m : ndarray of float, same shape as ``image``
        Local mean of the image.
    s : ndarray of float, same shape as ``image``
        Local standard deviation of the image.
    References
    ----------
    .. [1] F. Shafait, D. Keysers, and T. M. Breuel, "Efficient
           implementation of local adaptive thresholding techniques
           using integral images." in Document Recognition and
           Retrieval XV, (San Jose, USA), Jan. 2008.
           :DOI:`10.1117/12.767755`
    """
    if not isinstance(w, Iterable):
        w = (w,) * image.ndim
    # _validate_window_size(w) My only edit!

    pad_width = tuple((k // 2 + 1, k // 2) for k in w)
    padded = np.pad(image.astype('float'), pad_width,
                    mode='reflect')
    padded_sq = padded * padded

    integral = skimage.transform.integral.integral_image(padded)
    integral_sq = skimage.transform.integral.integral_image(padded_sq)

    kern = np.zeros(tuple(k + 1 for k in w))
    for indices in itertools.product(*([[0, -1]] * image.ndim)):
        kern[indices] = (-1) ** (image.ndim % 2 != np.sum(indices) % 2)

    total_window_size = np.prod(w)
    sum_full = ndi.correlate(integral, kern, mode='constant')
    m = skimage.util.crop(sum_full, pad_width) / total_window_size
    sum_sq_full = ndi.correlate(integral_sq, kern, mode='constant')
    g2 = skimage.util.crop(sum_sq_full, pad_width) / total_window_size
    # Note: we use np.clip because g2 is not guaranteed to be greater than
    # m*m when floating point error is considered
    s = np.sqrt(np.clip(g2 - m * m, 0, None))
    return m, s
