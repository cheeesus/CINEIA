import pandas as pd

def weighted_rating(x, m, C):
    """
    Calculates the weighted rating for a movie using the IMDB formula.

    Args:
        x (pd.Series): A row of the movies DataFrame.
        m (int): Minimum votes required to be listed.
        C (float): Mean vote across the whole report.

    Returns:
        float: The weighted rating.
    """
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)
