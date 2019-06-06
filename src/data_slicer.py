import itertools
import numpy as np


def data_slicer(plot_samples, x, y_points):
    """
    Sliced x and y data to correct lengths.
    If the number of points provided is less than plot_samples, padding with np.nan is provided (req for matplotlib only).
    Note that casting to lists is done after itertools.islice because many of the internal processing in
    matplotlib and pyqtgraph can not handle generators or other types of iterables.
    At least we slice to a plot_samples first to avoid creating giant lists.
    :param plot_samples:
    :param x:
    :param y_points:
    :return:
    """
    # Get length of data
    # Assumes all y data within a subplot is of the same length
    y_lengths = [len(y) for y in y_points]
    assert np.count_nonzero(np.diff(y_lengths)) == 0, "y data must all be of same length within a subplot."
    y_len = min(y_lengths[0], plot_samples)

    # Slice the data to the right number of samples
    y_points = [list(itertools.islice(y, max(len(y) - plot_samples, 0), None)) for y in y_points]
    x = list(itertools.islice(x, max(len(x) - plot_samples, 0), None))
    # Slice first, convert to list later.
    # This is faster and uses less memory if the iterable is a long non-slicable object (ex: deque)
    # A list is needed because we need to know the length.

    # Do the actual updating of the data, depending on blitting setting
    len_dif = plot_samples - y_len
    if len_dif > 0:
        y_points = tuple(np.array(list(itertools.chain((np.nan for _ in range(len_dif)), y))) for y in y_points)
        x = np.array(list(itertools.chain((np.nan for _ in range(len_dif)), x)))
    return x, y_points
