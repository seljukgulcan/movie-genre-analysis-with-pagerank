import networkx as nx
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm

DIFFERENT_ALPHA_POLICY = 0
SAME_ALPHA_POLICY = 1


def pagerank(base_dir='./', teleport_prob=0.15, *, disable_progress_bar=True, policy=DIFFERENT_ALPHA_POLICY):
    base_dir = Path(base_dir)

    movie_df = pd.read_csv(base_dir / 'movies.csv')
    movie_count = movie_df.shape[0]

    # Read edges
    edge_df = pd.read_csv(base_dir / 'edges.csv')
    df_append = pd.DataFrame({'source': edge_df['destination'],
                              'destination': edge_df['source'],
                              'weight': edge_df['weight']})
    edge_df = edge_df.append(df_append)

    print('Edges read')

    # Create the influence graph
    G = nx.from_pandas_edgelist(edge_df,
                                source='source',
                                target='destination',
                                edge_attr='weight',
                                create_using=nx.DiGraph)
    edge_df = None
    print('Graph generated')

    # Print some statistics for sanity check
    print(f'Edge count: {G.number_of_edges()}')
    print(f'Vertex count: {movie_count}')

    density = G.number_of_edges() / (movie_count * (movie_count - 1))

    print(f'Density: {density:.4f}')

    in_edge_count = [len(G.in_edges(idx)) for idx in movie_df['id']]
    in_edge_count = np.array(in_edge_count)

    out_edge_count = [len(G.out_edges(idx)) for idx in movie_df['id']]
    out_edge_count = np.array(out_edge_count)

    zero_in_edge_node_count = (in_edge_count == 0).sum()
    print(f'Nodes with 0 incoming edges : {zero_in_edge_node_count}')
    zero_out_edge_node_count = (out_edge_count == 0).sum()
    print(f'Nodes with 0 outgoing edges : {zero_out_edge_node_count}')

    # Normalize weights

    for i in tqdm(movie_df.index, disable=disable_progress_bar):
        total_w = sum(data['weight'] for u, v, data in G.out_edges(i, data=True))
        if total_w > 0:
            for u, v, data in G.out_edges(i, data=True):
                G[u][v]['weight'] = data['weight'] / total_w

    # Normal Pagerank
    alpha = 1 - teleport_prob
    result = nx.pagerank(G, weight='weight', alpha=alpha)
    movie_df['pagerank'] = pd.Series(result)

    print('Classic pagerank completed')

    # Creating personalization sets
    with open('genre.txt') as file:
        genre_set = set(line.strip() for line in file)

    genre2movies = {genre: [] for genre in genre_set}
    for movie_id, genre_str in zip(movie_df['id'], movie_df['genres']):
        genre_lst = genre_str.split('|')
        for genre in genre_lst:
            if genre in genre2movies:
                genre2movies[genre].append(movie_id)

    genre2count = {genre: len(movies) for genre, movies in genre2movies.items()}

    # Topic-specific Pagerank teleport set generation
    if policy == DIFFERENT_ALPHA_POLICY:
        # Different alpha values
        prob_teleport_each_movie = teleport_prob / genre2count['Thriller']
        genre2teleport_prob = {genre: prob_teleport_each_movie * count for genre, count in genre2count.items()}
        print(genre2teleport_prob)
        prob_teleport_each_movie = {genre: prob_teleport_each_movie for genre, count in genre2count.items()}
        print(prob_teleport_each_movie)
    else:
        # Same alpha value
        prob_teleport_each_movie = {genre: teleport_prob / count for genre, count in genre2count.items()}
        genre2teleport_prob = {genre: teleport_prob for genre, count in genre2count.items()}

    print('Teleport sets are created')

    # Topic-specific Pagerank
    for genre in tqdm(genre2movies, disable=disable_progress_bar):
        personalization_dict = {movie_id: 1 for movie_id in genre2movies[genre]}
        alpha = 1 - genre2teleport_prob[genre]
        result = nx.pagerank(G, alpha=alpha, weight='weight', personalization=personalization_dict)
        movie_df[genre] = pd.Series(result)

    return movie_df
