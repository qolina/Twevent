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

#include "cw.h"

using namespace std;

// global variables
char devfname[1024]; 				// development data
int k = 1;							// update the k-best prototypes
const char	USAGE[] = "Usage: cw_multiclass_learn [OPTIONS] input model\n"
						"Trains a linear classifier using the confidence-weighted algorithm.\n\n"
						"Options:\n"
						"  -C AGGRESS      Aggressiveness parameter. Default 0.01.\n"
						"  -k CONSTR       Use k-best contraints during update. Default 1.\n"
						"  -r VAR          Initial variance parameter. Default is 1.0\n"
						"  -e EPOCHS       Number of epochs. Default 1.\n"
						"  -f FORMAT       Input format: 1 (atomic feature, default) or 2 (libsvm feature-value pairs) or 3 (string:value pairs).\n"
						"  -p LINES        Print verbose message every LINES lines. Default is 10,000.\n"
						"  -a              Average weights of last epoch.\n"
						"  -m MISTAKES     Write number predictions mistakes to file MISTAKES.\n"
						"  -l MODEL        Load initial model from file MODEL.\n"
						"  -d DEVELOP	   Development set.\n"
						"  -b BIAS         Value of constant bias feature. Default is 1.0.\n"
						"  -n              Normalize final model. Default false.\n"
						"  -v              Print verbose output.\n"
						"  -h              Print this help message and exit.\n";


int print_usage() {
	cerr << USAGE << endl;
	return 0;
}

int f_xy(feat_vec & f_xy, const feat_vec & x, int y) {
	// block representation of features
	f_xy.clear();
	for (size_t i = 0; i < x.size(); i++) {
		f_xy.push_back(make_pair(x[i].first + (y * N), x[i].second));
	}
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


int get_dimensions(const char* file_name) {
	string token, line_string;
	int y_max = 0;
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
			int y = atoi(token.c_str());
			if (y > y_max)
				y_max = y;
		} else {
			cerr << "Error: illegal input file format.";
			fin.close();
			exit(-1);
		}

		while (line >> id >> sep >> val) {
			if (id > id_max)
				id_max = id;
		}
	}
	// set global variables
	K = y_max;
	N = id_max + 1; // +1 to include bias feature

	// clean up
	fin.close();
	return 0;
}

int build_index(const char* file_name, int format) {
	string token;
	ifstream fin(file_name);
	if (!fin.is_open()) {
		cerr << "Unable to open input file." << file_name << endl;
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

	map<string, int>::iterator iter;
	int i;
	// IMPORTANT: klass index starts at 0 and feature index at 1 (0 is reserved for bias feature)
	for (i = 0, iter = klass_index.begin(); iter != klass_index.end(); i++, iter++) {
		iter->second = i;
	}
	K = i;
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
			k = atoi(token.c_str()) -1;			// IMPORTANT: minus 1 for internal representation
			if (k < 0 or k >= K) {
				cerr << "Error: klass label must be a positive integer between 1 and " << K
						<< endl;
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
			// Ignore too large ids
			if (id < N)
				instance_vector.x.push_back(make_pair(id, val));
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


int update_mean(const feat_vec & g, const double alpha, bool averageThis, int n) {
	// perform update averaged weights
	if (averageThis) {
		update_avg(u_touch, n, g);
	}
	for (size_t i = 0; i < g.size(); i++) {
		u[g[i].first] += alpha * E[g[i].first] * g[i].second;
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

int update_variance(const feat_vec & g, const double alpha) {
	for (size_t i = 0; i < g.size(); i++) {
	  E[g[i].first] =  1.f / (1.f /E[g[i].first] +  2.f * alpha * C * g[i].second * g[i].second);
	}
	return 0;
}

pair<int, double> classify(const instance & instance_vector) {
	int y_hat = -1;
	int y = 0;
	double m_max = 0.0;
	double m = 0.0;
	for (y = 0; y < K; y++) {
		feat_vec fxy;
		f_xy(fxy, instance_vector.x, y);
		m = get_margin(fxy);
		if (y_hat < 0 || m > m_max) {
			y_hat = y;
			m_max = m;
		}
	}
	return make_pair(y_hat, m_max);
}



int k_best(vector<pair<int, double> > & kbest, const instance & instance_vector, size_t k, bool exclude_y) {
  kbest.clear();
  for (int y = 0; y < K; y++) {
    feat_vec fxy;
    f_xy(fxy, instance_vector.x, y);
    double m = get_margin(fxy);
    if (exclude_y && y == instance_vector.y) {
      continue;
    }
    kbest.push_back(make_pair(y, m));
  }
  sort(kbest.begin(), kbest.end(), cmp_pairs);
  kbest.resize(min(k, K));
  return 0;
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


int train_epoch(const char* training_file,
		const vector<instance> & dev_set, bool averageThis) {
	ifstream fin(training_file);
	string line;
	instance instance_vector;
	float dev_accuracy = 0.f;
	int y_hat;
	int n = 0;

	// initialize 'last touched' index
	if (averageThis) {
		for (size_t i = 0; i < N * K; i++) {
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
		if (verbose && n % (PRINT_LINES/ PRINT_DOTS) == 0) {
			cerr << ".";
			if (n % PRINT_LINES == 0) {
				cerr << n ;
				if (dev_set.size() > 0) {
					dev_accuracy = test_accuracy(dev_set);
					cerr << "\t\taccuracy: "  << dev_accuracy;
				}
				cerr << endl;
			}
		}

		// sequential many-contraints updates
		vector<pair<int, double> > kbest;
		k_best(kbest, instance_vector, k, true);
		feat_vec fxy;
		f_xy(fxy, instance_vector.x, instance_vector.y);
		for (size_t i=0; i< kbest.size(); i++) {
		  feat_vec g;
		  feat_vec fxk;
		  f_xy(fxk, instance_vector.x, kbest[i].first);
		  // indexes in fxy and fxy_hat are mutually exclusive
		  for (size_t j = 0; j < fxy.size(); j++)
		    g.push_back(fxy[j]);
		  for (size_t j = 0; j < fxk.size(); j++)
		    g.push_back(make_pair(fxk[j].first, -fxk[j].second));

		  // langrange
		  double M = get_margin(g);
		  double V = get_variance(g);
		  double b = 1.f + 2 * C * M;
		  double gamm = (-b + sqrt(b * b - 8 * C * (M - C * V))) / (4.f * C * V);
		  if (gamm > 0) {
			  // perform update
			  update_mean(g, gamm, averageThis, n);
			  update_variance(g, gamm);
		  }
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
		cerr << "accuracy: "  << dev_accuracy;
		cerr << endl;
	}

	// clean up
	fin.close();
	return 0;
}

int train(const char* training_file) {
	vector<instance> dev_set;

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
		train_epoch(training_file, dev_set, averageThis);
	}

	// clean up
	if (verbose)
		cerr << endl;
	return 0;
}

int init_model() {
	// initialize weights
	u.clear();
	u_avg.clear();
	E.clear();
	for (size_t i = 0; i < N * K; i++) {
		u.push_back(0.f);
		u_avg.push_back(0.f);
		E.push_back(initial_var);
	}
	return 0;
}


int load_model(const char* model_file) {
	ifstream fin(model_file);
	string line;

	if (!fin.is_open()) {
		cerr << "Unable to open model file. Exit." << endl;
		assert(false);
	}

	// read input format
	fin >> line;
	if ("==inputformat==" != line) {
		cerr << "Format error in model file , expected '==inputformat==' but was '"  << line << "'" << endl;
		assert(false);
	}
	fin >> input_format;
	// read dimensions
	fin >> line;
	if ("==#classes==" != line) {
		cerr << "Format error in model file , expected '==#classes==' but was '"  << line << "'" << endl;
		assert(false);
	}
	fin >> K;
	fin >> line;
	if ("==#features==" != line) {
		cerr << "Format error in model file , expected '==#features== but was '"  << line << "'" << endl;
		assert(false);
	}
	fin >> N;

	// read bias
	fin >> line;
	if ("==bias==" != line) {
		cerr << "Format error in model file , expected '==bias== but was '"  << line << "'" << endl;
		assert(false);
	}
	fin >> bias;

	// read klass and features index, if necessary
	if (input_format == 1 || input_format == 3) {
		fin >> line;
		if ("==klassmap==" != line) {
			cerr << "Format error in model file , expected '==klassmap== but was '"  << line << "'" << endl;
			assert(false);
		}
		string token;
		int id;
		// read klass index
		for (size_t y = 0; y < K; y++) {
			fin >> token;
			fin >> id;
			klass_index[token] = id;
		}
		// read feature index
		fin >> line;
		if ("==featuremap==" != line) {
			cerr << "Format error in model file , expected '==featuremap== but was '"  << line << "'" << endl;
			assert(false);
		}
		for (size_t i = 0; i < N - 1; i++) {			// bias feature not included
			fin >> token;
			fin >> id;
			feature_index[token] = id;
		}
	}
	// read weights
	fin >> line;
	if ("==weights==" != line) {
		cerr << "Format error in model file , expected '==weights== but was '"  << line << "'" << endl;
		assert(false);
	}
	double v;
	u.clear();
	for (size_t i = 0; i < K*N; i++) {
		bool b = fin >> v;
		if (b == false) {
			cerr  << "Format error in model file, too few weight values.";
			assert(false);
		}
		u.push_back(v);
	}

	// read covariance
	fin >> line;
	if ("==covariance==" != line) {
		cerr << "Format error in model file , expected '==covariance=='	but was '"  << line << "'" << endl;
		assert(false);
	}
	E.clear();
	for (size_t i = 0; i < K*N; i++) {
		bool b = fin >> v;
		if (b == false) {
			cerr  << "Format error in model file, too few covariance values.";
			assert(false);
		}
		E.push_back(v);
	}
	// clean up
	fin.close();

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
	fout << "==#classes==" << endl;
	fout << K << endl;
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
	for (size_t i = 0; i < K*N; i++) {
		if (averaged) {
			fout << u_avg[i] << endl;
		} else {
			fout << u[i] << endl;
		}
	}
	// write covariance
	fout << "==covariance==" << endl;
	for (size_t i = 0; i < K*N; i++) {
		fout << E[i] << endl;
	}
	// clean up
	fout.close();
	return 0;
}

int main(int argc, char **argv) {
	char c;
	char inputfname[1024], modelfname[1024], loadfname[1024];
	bool load_from_file = false;

	while ((c = getopt(argc, argv, "C:k:r:e:p:d:l:af:b:nvh")) != -1) {
		switch (c) {
		case 'C':
			C = atof(optarg);
			break;
		case 'k':
			k = atoi(optarg);
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
		case 'l':
			strcpy(loadfname, optarg);
			load_from_file = true;
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
		if (load_from_file) {
			cerr << "Load model   : " << loadfname << endl;
		}
	}

	// let's go
	if (load_from_file) {
		// load model
		if (verbose)
			cerr << "Load model.. ";
		load_model(loadfname);
		if (verbose)
			cerr << "done." << endl;
	} else {
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
		// init weights to zero
		init_model();
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
		cerr << "Save model.. " ;
	save_model(modelfname);
	if (verbose)
		cerr << "done." << endl;

	return 0;
}
