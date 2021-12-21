from pathlib import Path
import pandas as pd


def clean(base_dir='./'):

    base_dir = Path(base_dir)

    movie_df = pd.read_csv(base_dir / 'movies.csv')
    link_df = pd.read_csv(base_dir / 'links.csv')

    movie_df['imdb_id'] = link_df['imdbId']
    movie_df['tmdb_id'] = link_df['tmdbId']
    movie_df = movie_df.rename(columns={'movieId': 'movielens_id'})
    movie_df.to_csv(base_dir / 'movies.csv', index_label='id')

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
            file.write(f'{genre}\n')

    # Ratings cleaning
    rating_df = pd.read_csv(base_dir / 'ratings.csv')
    del rating_df['timestamp']

    movilens2id = pd.DataFrame(data=movie_df.index, index=movie_df['movielens_id'])
    rating_df['movieId'] = movilens2id.loc[rating_df['movieId']].values

    id2movielens = pd.Series(rating_df['userId'].drop_duplicates().sort_values().values)
    movielens2id = pd.Series(data=id2movielens.index, index=id2movielens)
    rating_df['userId'] = movielens2id.loc[rating_df['userId']].values

    rating_df = rating_df.rename(columns={'userId': 'user_id'})
    rating_df = rating_df.rename(columns={'movieId': 'movie_id'})

    # Writing mtx file
    row_count = rating_df['user_id'].max() + 1
    col_count = rating_df['movie_id'].max() + 1
    nnz_count = rating_df.shape[0]

    with open(base_dir / 'ratings.mtx', 'w') as file:
        file.write(f'{row_count} {col_count} {nnz_count}\n')
        rating_df.to_csv(file, index=False, sep=' ', header=False)

    Path(base_dir / 'ratings.csv').unlink()
    Path(base_dir / 'links.csv').unlink()
