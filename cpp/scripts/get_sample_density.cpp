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

    double threshold = 0.4;

    cout << "sets are created" << endl;

    uint thread_count = omp_get_max_threads();

    cout << "running on " << thread_count << " threads" << endl;

    vector<vector<Coord>> thread2edge_list(thread_count);
    vector<uint> thread2edge_count(thread_count, 0);
    vector<vector<float>> thread2weight_list(thread_count);

    #pragma omp parallel for schedule(dynamic, 100)
    for(uint i = 0; i < movie_count; i++)
    {
        int tid = omp_get_thread_num();

        if(i % 1000 == 0)
            cout << i << endl;

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

            float weight = (float(intersection)) / min(set_i.size(), set_j.size());

            if(i % 500 == 250)
            {
                thread2weight_list[tid].push_back(weight);
            }

            thread2edge_count[tid] += 2;
        }
    }

    // Merge edge counts
    uint edge_count = 0;
    for(uint i = 0; i < thread_count; i++)
    {
        edge_count += thread2edge_count[i];
    }

    // Merge weight vectors
    vector<float> weight_list;
    for(uint i = 0; i < thread_count; i++)
    {
        for(float weight : thread2weight_list[i])
        {
            weight_list.push_back(weight);
        }
    }
    cout << "Sampled weight count: " << weight_list.size() << endl;

    ofstream file("../weight_list.txt");

    for(float weight : weight_list)
    {
        file << weight << endl;
    }

    file.close();

    cout << edge_count << endl;

    double density = ((double)edge_count) / (movie_count * (movie_count - 1));
    cout << density << endl;
}