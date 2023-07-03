import numpy as np


def substract_arrays(arr_1, arr_2):
    """substract arr_2 to arr_1. arr_2[0] is a number, and is substracted to arr_1[0], which is a list

    Args:
        arr_1 (list of list): 
        arr_2 (list of numbers)

    Returns:
        list of list: substracted list
    """

    arr_2 = np.array(arr_2).reshape(len(arr_2), 1) if arr_2 else arr_2

    data = np.array(arr_1)

    data = data - arr_2 if arr_2 is not None else data

    return data
