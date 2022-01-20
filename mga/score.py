import numpy as np


def get_genre_scores(movie_df, genre_set):
    """
    Calculates genre scores from Topic-Specific Pagerank values. Refer to the project report for a bit more detailed
    explanation on how the scoress are calculated.
    :param movie_df: Movie dataframe with Topic-Specific Pagerank values, this is the output of mga.pagerank method
    :param genre_set: Set of genres
    :return: DataFrame similar to movie_df. Values in 'genre' columns are replaced with genre scores.
    """
    genre_column_lst = []
    for genre in genre_set:
        genre_column_lst.append(genre)
    genre_column_lst.append('pagerank')
    score_df = movie_df.drop(columns=genre_column_lst)

    for genre in genre_set:
        x = np.array(movie_df['pagerank'])
        y = np.array(movie_df[f'{genre}'])
        m, b = np.polyfit(x, y, deg=1)
        new_y = y / (m * x + b)

        score_df[genre] = new_y - 1

    return score_df
