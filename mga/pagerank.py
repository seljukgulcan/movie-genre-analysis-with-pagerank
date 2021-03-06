import sknetwork as skn
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
from scipy.sparse import coo_matrix

DIFFERENT_ALPHA_POLICY = 0
SAME_ALPHA_POLICY = 1


def pagerank(base_dir='./', teleport_prob=0.15, *, disable_progress_bar=True, policy=DIFFERENT_ALPHA_POLICY,
             unlabeled_movie_set=None, symmetric=False):
    """
    Pagerank calculations using scikit-network. This is more memory efficient than networkx Pagerank method
    (pagerank). The method calculates base Pagerank value and Topic-Specific Pagerank value for each genre.
    These pagerank values can be given to mga.get_genre_scores method to generate score values for each genre.
    :param base_dir: Base directory of movies.csv and edges.csv files
    :param teleport_prob: Teleport probability of random surfer
    :param disable_progress_bar: False value hides the progress bar
    :param policy:
    :param unlabeled_movie_set: Movies in this set are removed from teleport sets in topic-specific pagerank.
    :param symmetric: If true it creates symmetric adjacency matrix. Set it to True if w(u, v) exists, w(v, u) does not
    exist but w(v, u) should exist.
    I use it for genre classification
    :return:
    """
    base_dir = Path(base_dir)

    if unlabeled_movie_set is None:
        unlabeled_movie_set = set()

    movie_df = pd.read_csv(base_dir / 'movies.csv')
    movie_count = movie_df.shape[0]

    # Read edges

    G = coo_matrix((movie_count, movie_count), dtype='f')
    for chunk in pd.read_csv(base_dir / 'edges.csv', chunksize=100_000):
        temp = coo_matrix((chunk['weight'], (chunk['source'], chunk['destination'])),
                          shape=(movie_count, movie_count),
                          dtype='f')
        G += temp
    print('Edges read')

    # Create the influence graph
    if symmetric:
        G = G + G.T
    G = G.tocsr()
    print('Graph generated')

    # Print some statistics for sanity check
    edge_count = G.nnz
    print(f'Edge count: {edge_count}')
    print(f'Vertex count: {movie_count}')

    density = edge_count / (movie_count * (movie_count - 1))

    print(f'Density: {density:.4f}')

    zero_in_edge_node_count = (G.sum(axis=0) == 0).sum()
    print(f'Nodes with 0 incoming edges : {zero_in_edge_node_count}')
    zero_out_edge_node_count = (G.sum(axis=1) == 0).sum()
    print(f'Nodes with 0 outgoing edges : {zero_out_edge_node_count}')

    # Normalize weights
    row_sum = np.asarray(G.sum(axis=1)).squeeze()
    row_sum[row_sum == 0] = 1
    G.data /= row_sum[G.nonzero()[0]]

    # Normal Pagerank
    damping_factor = 1 - teleport_prob

    pagerank = skn.ranking.pagerank.PageRank(damping_factor=damping_factor, n_iter=100)
    result = pagerank.fit_transform(G)
    movie_df['pagerank'] = pd.Series(result)

    print('Classic pagerank completed')

    # Creating personalization sets
    with open('genre.txt') as file:
        genre_set = set(line.strip() for line in file)

    genre2movies = {genre: [] for genre in genre_set}
    for movie_id, genre_str in zip(movie_df['id'], movie_df['genres']):

        if movie_id in unlabeled_movie_set:
            continue

        genre_lst = genre_str.split('|')
        for genre in genre_lst:
            if genre in genre2movies:
                genre2movies[genre].append(movie_id)

    genre2count = {genre: len(movies) for genre, movies in genre2movies.items()}

    # Topic-specific Pagerank teleport set generation
    if policy == DIFFERENT_ALPHA_POLICY:
        # Different alpha values
        # TODO: This part can be improved, right now we choose Thriller as baseline genre. Other genres
        # calculate teleport probability with respect to Thriller. It's fine for M25 dataset since Thriller movie
        # count gives a nice average, but for other datasets, we should adopt more statistically correct approach.
        prob_teleport_each_movie = teleport_prob / genre2count['Thriller']
        genre2teleport_prob = {genre: prob_teleport_each_movie * count for genre, count in genre2count.items()}
    else:
        # Same alpha value
        genre2teleport_prob = {genre: teleport_prob for genre, count in genre2count.items()}

    print('Teleport sets are created')

    # Topic-specific Pagerank
    for genre in tqdm(genre2movies, disable=disable_progress_bar):
        personalization_dict = {movie_id: 1 for movie_id in genre2movies[genre]}
        damping_factor = 1 - genre2teleport_prob[genre]

        pagerank = skn.ranking.PageRank(damping_factor=damping_factor, n_iter=100)
        result = pagerank.fit_transform(G, seeds=personalization_dict)
        movie_df[genre] = pd.Series(result)

    return movie_df
