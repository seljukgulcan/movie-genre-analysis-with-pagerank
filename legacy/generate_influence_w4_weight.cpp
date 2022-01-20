#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <unordered_set>
#include <set>
#include <omp.h>
#include <algorithm>

#include "util.h"

#define SET unordered_set

using namespace std;

vector<Coord> read_mtx_file(string mtx_filename, uint& row_count, uint& col_count)
{
    uint nnz_count;
    ifstream file(mtx_filename);

    if(!file.good())
        throw std::runtime_error("Cannot read file, invalid mtx file");

    string line;
    getline(file, line);
    while(line[0] == '%')
        getline(file, line);

    int i = 0;
    while(line[i] != ' ')
        i++;
    row_count = stoi(line.substr(0, i));
    int j = i + 1;
    while(line[j] != ' ')
        j++;
    col_count = stoi(line.substr(i + 1, j));
    nnz_count = stoi(line.substr(j + 1));

    vector<Coord> retval(nnz_count);

    for(uint i = 0; i < nnz_count; i++)
    {
        uint row, col;
        float rating;

        file >> row >> col >> rating;
        retval[i].row = row;
        retval[i].col = col;
        retval[i].weight = rating;
    }

    file.close();

    return retval;
}


int main(int argc, char** argv)
{
    if(argc < 2)
    {
        cout << "Usage: " << argv[0] << " <filename>" << endl;
    }

    cout << "w_4 weight calculation" << endl;

    string filename = argv[1];

    cout << filename << endl;

    vector<Coord> rating_arr;
    uint user_count, movie_count, rating_count;
    rating_arr = read_mtx_file(filename, user_count, movie_count);
    rating_count = rating_arr.size();

    cout << user_count << endl;
    cout << movie_count << endl;
    cout << rating_count << endl;

    vector<SET<uint>> movie2userset(movie_count);

    cout << "file read" << endl;

    for(uint i = 0; i < rating_arr.size(); i++)
    {
        uint user = rating_arr[i].row;
        uint movie = rating_arr[i].col;

        movie2userset[movie].insert(user);
    }

    double threshold = 0.25;

    cout << "sets are created" << endl;

    uint thread_count = omp_get_max_threads();

    cout << "running on " << thread_count << " threads" << endl;

    cout << "threshold: " << threshold << endl;

    vector<vector<Coord>> thread2edge_list(thread_count);

    #pragma omp parallel for schedule(dynamic, 30)
    for(uint i = 0; i < movie_count; i++)
    {
        int tid = omp_get_thread_num();

        SET<uint>& set_i = movie2userset[i];
        for(uint j = i + 1; j < movie_count; j++)
        {
            SET<uint>& set_j = movie2userset[j];
            if(set_i.size() == 0 || set_j.size() == 0)
                continue;

            uint intersection = 0;
            for (auto i = set_j.begin(); i != set_j.end(); i++) {
                if (set_i.find(*i) != set_i.end())
                {
                    intersection += 1;
                }
            }

            if(intersection == 0)
                continue;

            float w1 = (float(intersection)) / set_j.size();
            float w2 = (float(intersection)) / set_i.size();
            if(w1 > threshold)
            {
                Coord edge1;
                edge1.row = i;
                edge1.col = j;
                edge1.weight = w1;

                thread2edge_list[tid].push_back(edge1);
            }

            if(w2 > threshold)
            {
                Coord edge2;
                edge2.row = j;
                edge2.col = i;
                edge2.weight = w2;

                thread2edge_list[tid].push_back(edge2);
            }
        }
    }

    // Merge edge vectors
    vector<Coord> edge_list;
    for(uint i = 0; i < thread_count; i++)
    {
        for(Coord edge : thread2edge_list[i])
        {
            edge_list.push_back(edge);
        }
    }
    uint edge_count = 2 * edge_list.size();

    cout << "Edge count: " << edge_count << endl;
    double density = ((double)edge_count) / (movie_count * (movie_count - 1));
    cout << "Density: " << density << endl;

    ofstream file("edges.csv");
    file << "source,destination,weight" << endl;
    for(Coord edge : edge_list)
    {
        file << edge.row << "," << edge.col << "," << edge.weight << endl;
    }

    file.close();
}
