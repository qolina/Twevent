/*
 Licensed to the Apache Software Foundation (ASF) under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  The ASF licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing,
 software distributed under the License is distributed on an
 "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 KIND, either express or implied.  See the License for the
 specific language governing permissions and limitations
 under the License.
 */

#include "cw.h"

using namespace std;

// global variables
char plotfname[1024]; // output file for number of prediction mistakes
char devfname[1024]; // development data
const char USAGE[] = "Usage: cw_binary_learn [OPTIONS] input model\n"
						"Trains a linear classifier using the confidence-weighted algorithm.\n\n"
						"Options:\n"
						"  -C AGGRESS      Aggressiveness parameter. Default 0.01.\n"
						"  -r VAR          Initial variance parameter. Default is 1.0\n"
						"  -e EPOCHS       Number of epochs. Default 1.\n"
						"  -f FORMAT       Input format: 1 (atomic feature, default) or 2 (libsvm feature-value pairs) or 3 (string:value pairs).\n"
						"  -p LINES        Print verbose message every LINES lines. Default is 10,000.\n"
						"  -a              Average weights of last epoch. Default false\n"
						"  -m MISTAKES     Write number predictions mistakes to file MISTAKES.\n"
						"  -d DEVELOP	   Development set.\n"
						"  -b BIAS         Value of constant bias feature. Default is 1.0.\n"
						"  -n              Normalize final model. Default false.\n"
						"  -v              Print verbose output.\n"
						"  -h              Print this help message and exit.\n";

int print_usage() {
	cerr << USAGE << endl;
	return 0;
}


int normalize(double_vec & w) {
	double n = 0.0;
	for (size_t i = 0; i < w.size(); i++) {
		n += w[i] * w[i];
	}
	n = sqrt(n);
	for (size_t i = 0; i < w.size(); i++) {
		w[i] = w[i] / n;
	}
	return 0;
}

double norm(const feat_vec & x) {
	double n = 0.0;
	for (size_t i = 0; i < x.size(); i++) {
		n += x[i].second * x[i].second;
	}
	return n;
}

int get_dimensions(const char* file_name) {
	string token, line_string;
	int id_max = 0;
	int id = 0;
	char sep = 0;
	double val = 0.0;
	ifstream fin(file_name);
	if (!fin.is_open()) {
		cerr << "Unable to open input file:" << file_name << endl;
		exit(-1);
	}
	while (fin.good()) {
		getline(fin, line_string);
		if (line_string[0] == '\0' || line_string[0] == '#') // comment
			continue;
		istringstream line(line_string);
		if (line >> token) {
			if (token.compare("-1") != 0 and token.compare("+1") != 0
					and token.compare("1") != 0) {
				cerr << "Error: class label must either be +1 or -1." << endl;
				fin.close();
				exit(-1);
			}
		} else {
			cerr << "Error: empty line in input file." << endl;
			fin.close();
			exit(-1);
		}

		while (line >> id >> sep >> val) {
			if (id > id_max)
				id_max = id;
		}
	}
	// set global variables
	N = id_max + 1; // +1 to include bias feature

	// clean up
	fin.close();
	return 0;
}

int build_index(const char* file_name, int format) {
	string token;
	ifstream fin(file_name);
	if (!fin.is_open()) {
		cerr << "Error: unable to open input file." << file_name << endl;
		exit(-1);
	}
	klass_index.clear();
	feature_index.clear();

	while (fin.good()) {
		getline(fin, token);
		if (token[0] == '\0' || token[0] == '#') // comment
			continue;
		istringstream line(token);
		if (line >> token) {
			klass_index[token] = 1;
		}
		while (line >> token) {
			if (format == 3) {
				if ("|||" == token) {
					break;
				}
				int sep = token.rfind(":");
				feature_index[token.substr(0, sep)] = 1;
			} else if (format == 1) {
				if ("|||" == token) {
					break;
				}
				feature_index[token] = 1;
			}
		}
	}

	// klass index
	if (klass_index.size() != 2) {
		cerr << "Error: Found more than two class labels." << endl;
		exit(-1);
	}
	klass_index.begin()->second = -1;
	klass_index.end()->second = +1;

	// feature index
	map<string, int>::iterator iter;
	int i;
	for (i = 1, iter = feature_index.begin(); iter != feature_index.end(); i++, iter++) {
		iter->second = i;
	}
	N = i;

	//clean up
	fin.close();
	return 0;
}

int parse_line(const string & instance_line, instance & instance_vector) {
	string token;
	istringstream line(instance_line);
	map<string, int>::iterator iter;

	// reset instance vector
	instance_vector.y = 0;
	instance_vector.x.clear();

	if (line >> token) {
		int k;
		if (input_format == 1 || input_format == 3) {
			iter = klass_index.find(token);
			if (iter != klass_index.end())
				k = iter->second;
			else
				k = 0;
		} else if (input_format == 2) {
			if (token.compare("+1") == 0 or token.compare("1") == 0)
				k = 1;
			else if (token.compare("-1") == 0)
				k = -1;
			else {
				cerr << "Error: class label must be -1 or 1" << endl;
				assert(false);
			}
		} else {
			cerr << "Error: unknown input format: " << input_format << endl;
			assert(false);
		}
		instance_vector.y = k;
	}

	// bias feature
	instance_vector.x.push_back(make_pair(0, bias));

	if (input_format == 1) {
		// binary features for each token in input
		while (line >> token) {
			if ("|||" == token) {
				break;
			}
			iter = feature_index.find(token);
			// Ignore unknown features
			if (iter != feature_index.end())
				instance_vector.x.push_back(make_pair(iter->second, 1));
		}
	} else if (input_format == 2) {
		// lib-svm feature-value pairs
		int id = 0;
		char sep = 0;
		double val = 0.0;
		while (line >> id >> sep >> val) {
			assert (id > 0);
			// Ignore too large ids
			if (id < N) {
				instance_vector.x.push_back(make_pair(id, val));
			}
		}
	} else if (input_format == 3) {
		// feature : value pairs
		double val = 0.0;
		while (line >> token) {
			if ("|||" == token) {
				break;
			}
			int sep = token.rfind(":");
			iter = feature_index.find(token.substr(0, sep));
			// Ignore unknown features
			if (iter != feature_index.end()) {
				val = atof(token.substr(sep+1).c_str());
				instance_vector.x.push_back(make_pair(iter->second, val));
			}
		}
	} else {
		cerr << "Error: unknown input format: " << input_format << endl;
		assert(false);
	}
	return 0;
}

double get_margin(const feat_vec & x) {
	double m = 0.0;
	for (size_t i = 0; i < x.size(); i++) {
		m += u[x[i].first] * x[i].second;
	}
	return m;
}

double get_variance(const feat_vec & x) {
	double V = 0.0;
	for (size_t i = 0; i < x.size(); i++) {
		V += x[i].second * E[x[i].first] * x[i].second;
	}
	return V;
}

int update_mean(const feat_vec & x, const int y, const double alpha, bool averageThis, int n) {
	// perform update averaged weights
	if (averageThis) {
		update_avg(u_touch, n, x);
	}
	for (size_t i = 0; i < x.size(); i++) {
		u[x[i].first] += alpha * y * E[x[i].first] * x[i].second;
	}
	return 0;
}

int update_avg(double_vec & r_touch, const int r, const feat_vec & g) {
	for (size_t i = 0; i < g.size(); i++) {
		u_avg[g[i].first] += (r - r_touch[i]) * u[g[i].first];
		// keep track when weight was last updated
		r_touch[i] = r;
	}
	return 0;
}

int update_variance(const feat_vec & x, const double alpha) {
	for (size_t i = 0; i < x.size(); i++) {
		E[x[i].first] = 1.f / (1.f / E[x[i].first] + 2.f * alpha * C
				* x[i].second * x[i].second);
	}
	return 0;
}

pair<int, double> classify(const instance & instance_vector) {
	double m = get_margin(instance_vector.x);
	int y_hat = sign(m);
	return make_pair(y_hat, m);
}

double test_accuracy(const vector<instance> test_set) {
	int y_hat = -1;
	int correct = 0;
	// make prediction
	for (int i = 0; i < test_set.size(); i++) {
		pair<int, double> prediction = classify(test_set[i]);
		y_hat = prediction.first;
		correct += (y_hat == test_set[i].y) ? 1 : 0;
	}
	// accuracy
	float accuracy = (float) correct / (float) test_set.size();
	return accuracy;
}

int train_epoch(const char* training_file, int & train_errors, ofstream & fout,
		const vector<instance> & dev_set, bool averageThis) {
	ifstream fin(training_file);
	string line;
	instance instance_vector;
	float dev_accuracy = 0.f;
	int y_hat;
	int n = 0;
	double M = 0.0;
	double V = 0.0;
	double gamm = 0.0;

	// initialize 'last touched' index
	if (averageThis) {
		for (size_t i = 0; i < N; i++) {
			u_touch.push_back(0.f);
		}
	}

	if (!fin.is_open()) {
		cerr << "Unable to open input file:" << training_file << endl;
		exit(-1);
	}

	while (fin.good()) {
		// read next example
		getline(fin, line);
		if (line.empty() || line[0] == '#') // empty line or comment
			continue;

		// parse input
		parse_line(line, instance_vector);

		// print verbose
		n++;
		if (verbose && n % (PRINT_LINES / PRINT_DOTS) == 0) {
			cerr << ".";
			if (n % PRINT_LINES == 0) {
				cerr << n;
				if (dev_set.size() > 0) {
					dev_accuracy = test_accuracy(dev_set);
					cerr << "\t\taccuracy: " << dev_accuracy;
				}
				cerr << endl;
			}
		}

		// make prediction
		pair<int, double> prediction = classify(instance_vector);
		y_hat = prediction.first;
		if (y_hat != instance_vector.y) {
			// increase number of mistakes, write to fout, if fout
			train_errors++;
		}
		// write number of training errors, if fout
		if (fout.is_open()) {
			fout << train_errors << endl;
		}

		// langrange
		M = instance_vector.y * get_margin(instance_vector.x);
		V = get_variance(instance_vector.x);
		double b = 1.f + 2 * C * M;
		gamm = (-b + sqrt(b * b - 8 * C * (M - C * V))) / (4.f * C * V);
		if (gamm > 0) {
			// perform update
			update_mean(instance_vector.x, instance_vector.y, gamm, averageThis, n);
			update_variance(instance_vector.x, gamm);
		}
	}

	// one last update of the averaged weights
	if (averageThis) {
		for (size_t i = 0; i < u.size(); i++) {
			u_avg[i] += (n - u_touch[i]) * u[i];
		}
	}

	// test on dev
	if (dev_set.size() > 0) {
		dev_accuracy = test_accuracy(dev_set);
		cerr << "accuracy: " << dev_accuracy;
		cerr << endl;
	}

	// clean up
	fin.close();
	return 0;
}

int train(const char* training_file) {
	vector<instance> dev_set;
	int train_errors = 0;

	// initialise parameters
	for (size_t i = 0; i < N; i++) {
		u.push_back(0.f);
		u_avg.push_back(0.f);
		E.push_back(initial_var);
	}

	// open file for training error statistics, if given
	ofstream fout;
	if (plotfname[0] != '\0')
		fout.open(plotfname);

	// load development data, if given
	if (devfname[0] != '\0') {
		ifstream fdev;
		fdev.open(devfname);
		instance instance_vector;
		string line;

		if (!fdev.is_open()) {
			cerr << "Unable to open development file:" << devfname << endl;
			exit(-1);
		}
		while (fdev.good()) {
			// read examples
			getline(fdev, line);
			if (line.empty() || line[0] == '#') // empty line or comment
				continue;
			// parse input and add to development set
			parse_line(line, instance_vector);
			dev_set.push_back(instance_vector);
		}
		fdev.close();
	}

	// train epochs
	for (int epoch = 0; epoch < epochs; epoch++) {
		if (verbose)
			cerr << "\n====== Start epoch " << epoch << " ======" << endl;
		bool averageThis = (averaged && epoch == epochs-1) ? true : false;
		train_epoch(training_file, train_errors, fout, dev_set, averageThis);
	}

	// clean up
	if (verbose)
		cerr << endl;
	if (plotfname[0] != '\0')
		fout.close();
	return 0;
}

int save_model(const char* model_file) {
	ofstream fout(model_file);

	if (!fout.is_open()) {
		cerr << "Unable to write to output file. Exit." << endl;
		assert(false);
	}
	// write input format
	fout << "==inputformat==" << endl;
	fout << input_format << endl;

	// write dimensions
	fout << "==#features==" << endl;
	fout << N << endl;

	// write bias
	fout << "==bias==" << endl;
	fout << bias << endl;

	if (input_format == 1 || input_format == 3) {
		map<string, int>::iterator iter;
		// write klass index
		fout << "==klassmap==" << endl;
		for (iter = klass_index.begin(); iter != klass_index.end(); iter++) {
			fout << iter->first << " " << iter->second << endl;
		}
		// write feature index
		fout << "==featuremap==" << endl;
		for (iter = feature_index.begin(); iter != feature_index.end(); iter++) {
			fout << iter->first << " " << iter->second << endl;
		}
	}
	// write mean
	fout << "==weights==" << endl;
	for (size_t i = 0; i < N; i++) {
		if (averaged) {
			fout << u_avg[i] << endl;
		} else {
			fout << u[i] << endl;
		}
	}
	// write covariance
	fout << "==covariance==" << endl;
	for (size_t i = 0; i < N; i++) {
		fout << E[i] << endl;
	}
	// clean up
	fout.close();
	return 0;
}

int main(int argc, char **argv) {
	char c;
	char inputfname[1024], modelfname[1024];

	while ((c = getopt(argc, argv, "C:r:e:p:d:m:af:b:nvh")) != -1) {
		switch (c) {
		case 'C':
			C = atof(optarg);
			break;
		case 'r':
			initial_var = atof(optarg);
			break;
		case 'e':
			epochs = atoi(optarg);
			break;
		case 'f':
			input_format = atoi(optarg);
			break;
		case 'p':
			PRINT_LINES = atoi(optarg);
			break;
		case 'd':
			strcpy(devfname, optarg);
			break;
		case 'm':
			strcpy(plotfname, optarg);
			break;
		case 'b':
			bias = atof(optarg);
			break;
		case 'a':
			averaged = true;
			break;
		case 'n':
			normalized = true;
			break;
		case 'v':
			verbose = true;
			break;
		case 'h':
			print_usage();
			return (0);
		case '?':
			print_usage();
			return -1;
		default:
			print_usage();
			return -1;
		}
	}

	if (argc - optind != 2) {
		print_usage();
		return -1;
	}
	strcpy(inputfname, argv[optind++]);
	strcpy(modelfname, argv[optind++]);

	if (verbose) {
		cerr << "Input file   : " << inputfname << endl;
		cerr << "Model file   : " << modelfname << endl;
		cerr << "Epochs       : " << epochs << endl;
		cerr << "Input format : " << input_format << endl;
	}

	// let's go
	// build feature index or get dimensions
	if (input_format == 1 || input_format == 3) {
		if (verbose)
			cerr << "Build feature index..";
		build_index(inputfname, input_format);
		if (verbose)
			cerr << "done." << endl;
	} else if (input_format == 2) {
		if (verbose)
			cerr << "Get feature dimensions..";
		get_dimensions(inputfname);
		if (verbose)
			cerr << "done." << endl;
	} else {
		cerr << "Error: unknown input file format.";
		assert(false);
	}

	// train
	train(inputfname);

	// normalize
	if (normalized) {
		normalize(u);
		normalize(u_avg);
	}

	// save
	if (verbose)
		cerr << "Save model.. ";
	save_model(modelfname);
	if (verbose)
		cerr << "done." << endl;

	return 0;
}
