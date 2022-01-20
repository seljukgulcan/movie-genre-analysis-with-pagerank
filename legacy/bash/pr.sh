set -e

eval "$(conda shell.bash hook)"
conda activate cs529

PINGBIN=~/repo/script/ping.py

trap '${PINGBIN} "ERROR! in ${DATA}"' ERR

cd movie_project

${PINGBIN} "Movie genre pagerank started"

python run_pagerank.py

${PINGBIN} "Movie genre pagerank completed"