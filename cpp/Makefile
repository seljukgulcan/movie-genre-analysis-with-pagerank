CC = g++

EXEC = generate
SOURCE = *.cpp
CFLAGS = -std=c++11 -Wall -fopenmp -O3 -ftree-vectorize -fopt-info-vec -mavx2

$(EXEC): $(SOURCE)
	$(CC) $(CFLAGS) -o $(EXEC) $^ -ldl

.PHONY: clean
clean:
	rm $(EXEC)
