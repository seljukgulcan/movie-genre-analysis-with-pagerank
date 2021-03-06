from mga.pagerank import pagerank
from mga.score import get_genre_scores

from pathlib import Path
import pandas as pd


def clean(base_dir='./', movie_view_threshold=15):
    """
    Preprocesses downloaded movielens dataset by using movies.csv, links.csv, genre.txt files. After the preprocessing,
    the method produces movies.csv and ratings.mtx files. The ratings.mtx file should be fed into
    generate_influence_graph script to produce movie influence graph (edges.csv).
    :param base_dir: Directory where dataset files are extracted. This path should contain movies.csv and
    links.csv files
    :param movie_view_threshold: Movies with less view count than this number are removed. Removing movies with
    low view count helps the performance of pagerank by producing more sparse movie influence graph
    :return: None
    """

    base_dir = Path(base_dir)

    movie_df = pd.read_csv(base_dir / 'movies.csv')
    link_df = pd.read_csv(base_dir / 'links.csv')

    movie_df['imdb_id'] = link_df['imdbId']
    movie_df['tmdb_id'] = link_df['tmdbId']
    movie_df = movie_df.rename(columns={'movieId': 'movielens_id'})

    # Genre cleaning
    genre_set = set()
    for genre_str in movie_df['genres']:
        genre_lst = genre_str.split('|')
        for genre in genre_lst:
            genre_set.add(genre)

    no_genre_key = '(no genres listed)'

    count_movie_with_no_genre = sum(movie_df['genres'] == no_genre_key)
    print(f'Total number of movies with no genre: {count_movie_with_no_genre}')
    genre_set.remove(no_genre_key)

    ignored_genre_set = {'IMAX', 'Film-Noir', 'Animation', 'Documentary'}

    print(f'Genres ({len(genre_set)}): {genre_set}')
    print(f'Ignored genres: {ignored_genre_set}')

    with open(base_dir / 'genre.txt', 'w') as file:
        for genre in genre_set:
            if genre not in ignored_genre_set:
                file.write(f'{genre}\n')

    # Ratings cleaning
    rating_df = pd.read_csv(base_dir / 'ratings.csv')
    del rating_df['timestamp']
    rating_df = rating_df.rename(columns={'userId': 'user_id', 'movieId': 'movie_id'})

    # Get movies with view count larger than the threshold
    df_count = rating_df[['movie_id', 'rating']].groupby('movie_id').aggregate(['count'])
    df_count.columns = df_count.columns.droplevel()
    df_count = df_count.loc[df_count['count'] > movie_view_threshold]

    # Filter rating df
    rating_df = rating_df[rating_df['movie_id'].isin(df_count.index)]

    # Filter movie df and reset index
    old_movie_count = movie_df.shape[0]
    movie_df = movie_df[movie_df['movielens_id'].isin(df_count.index)]
    movie_df = movie_df.reset_index(drop=True)
    new_movie_count = movie_df.shape[0]
    dropped_movie_count = old_movie_count - new_movie_count
    print(f'Dropped movie count: {dropped_movie_count}')
    print(f'New movie count: {new_movie_count}')

    movilens2id = pd.DataFrame(data=movie_df.index, index=movie_df['movielens_id'])
    rating_df['movie_id'] = movilens2id.loc[rating_df['movie_id']].values

    id2movielens = pd.Series(rating_df['user_id'].drop_duplicates().sort_values().values)
    movielens2id = pd.Series(data=id2movielens.index, index=id2movielens)
    rating_df['user_id'] = movielens2id.loc[rating_df['user_id']].values

    movie_df.to_csv('movies.csv', index_label='id')

    # Writing mtx file
    row_count = rating_df['user_id'].max() + 1
    col_count = rating_df['movie_id'].max() + 1
    nnz_count = rating_df.shape[0]

    with open(base_dir / 'ratings.mtx', 'w') as file:
        file.write(f'{row_count} {col_count} {nnz_count}\n')
        rating_df.to_csv(file, index=False, sep=' ', header=False)

    Path(base_dir / 'ratings.csv').unlink()
    Path(base_dir / 'links.csv').unlink()
