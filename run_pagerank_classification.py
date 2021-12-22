import pandas as pd
import numpy as np

import mga

DEFAULT_TELEPORT_PROB = 0.25

if __name__ == '__main__':
    movie_df = pd.read_csv('movies.csv')
    unlabeled_movie_lst = np.random.choice(movie_df['id'], size=1000, replace=False)
    with open('unlabeled.txt', 'w') as file:
        for movie_id in unlabeled_movie_lst:
            file.write(f'{movie_id}\n')
    unlabeled_movie_set = set(unlabeled_movie_lst)

    df = mga.pagerank(base_dir='./', teleport_prob=DEFAULT_TELEPORT_PROB, disable_progress_bar=True,
                      unlabeled_movie_set=unlabeled_movie_set)
    df.to_csv('movies_pr_classification.csv')
