/*
 Copyright 2011 Daniel Dahlmeier

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
*/

#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <string>
#include <getopt.h>
#include <sstream>
#include <cstdlib>
#include <cassert>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <algorithm>

#ifndef CW_H_
#define CW_H_

using namespace std;

// data structures
typedef vector<pair<int, double> > feat_vec;
typedef vector<double> double_vec;
typedef struct {
	int y;
	feat_vec x;
} instance;

// global variables
size_t K = 0; 					// number of klasses
size_t N = 0; 					// feature dimension
map<string, int> klass_index; 	// map from klass labels to numeric klass id
map<string, int> feature_index; // map from feature labels to numeric feature id
int PRINT_LINES = 10000; 		// print verbose message every PRINT_LINES lines
const int PRINT_DOTS = 40; 		// number of dots per line in verbose message
int epochs = 1; 				// number of iterations over the data
int input_format = 1;			// format: raw features tokens (1) or index:value pairs (2)
double bias = 1.0; 				// constant bias feature
bool verbose = false; 			// verbose output
bool averaged = false;			// average weights
bool normalized = false;        // normalize final model to unit length
double_vec u; 					// the mean of distribution over weight vectors
double_vec u_touch; 				// keep track in which weights were last updated
double_vec u_avg; 				// the averaged weight vectors
double_vec E; 					// the diagonal covariance matrix of the distribution
double C = 0.01; 				// confidence parameter = Psi^(-1) (eta)
double initial_var = 1.0; 		// initial variance parameter a > 0

//prototypes
int print_usage();
double norm(const feat_vec & x);
int get_dimensions(const char* file_name);
int build_index(const char* file_name, int format);
int parse_line(const string & instance_line, instance & instance_vector);
double get_margin(const feat_vec & x);
double get_variance(const feat_vec & x);
int update_mean(const feat_vec & x, const int y, const double alpha, bool averageThis, int n);
int update_mean(const feat_vec & x, const double alpha, bool averageThis, int n);
int update_avg(double_vec & r_touch, int r, const feat_vec & g);
int update_variance(const feat_vec & x, const double alpha);
pair<int, double> classify(const instance & instance_vector);
double test_accuracy(const vector<instance> test_set);
int train_epoch(const char* training_file, int & train_errors, ofstream & fout,
		const vector<instance> & dev_set, bool averageThis);
int train(const char* training_file);
int test(const char* test_file, const char* output_file);
int init_model();
int save_model(const char* model_file);
int load_model(const char* model_file);
int normalize(double_vec & w);
bool cmp_pairs(pair<int, double> a, pair<int, double> b) { return a.second > b.second;};
int sign(double x) {return (x > 0.0) ? 1 : -1;};

#endif /* CW_H_ */

