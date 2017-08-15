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
map<int, string> klass_rindex;	// mapping from internal class index to class labels
bool detailed_output = false; 	// print confidence
const char	USAGE[] = "Usage: cw_classify [OPTIONS] input model output\n"
						"Classify instances in input with a linear model.\n\n"
						"Options:\n"
						"  -d              Detailed score with confidence score.\n"
						"  -h              Print this help message and exit.\n";

int print_usage() {
	cerr << USAGE << endl;
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
		int k = 0;
		if (input_format == 1 || input_format == 3) {
			k = klass_index[token];
		} else if (input_format == 2) {
			if (token.compare("+1") == 0 or token.compare("1") == 0)
				k = 1;
			else if (token.compare("-1") == 0)
				k = -1;
		} else {
			cerr << "Error: unknown input format: " << input_format << endl;
			assert(false);
		}
		instance_vector.y = k;
	}

	// bias feature
	instance_vector.x.push_back(make_pair(0, bias));

	if (input_format == 1) {
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

pair<int, double> classify(const instance & instance_vector) {
	double m = get_margin(instance_vector.x);
	int y_hat = sign(m);
	return make_pair(y_hat, m);
}

int test(const char* test_file, const char* output_file) {
	ifstream fin(test_file);
	ofstream fout(output_file);
	string line, label;
	instance instance_vector;
	int y_hat;
	double confidence;
	int total = 0;
	int correct = 0;

	if (!fin.is_open()) {
		cerr << "Unable to open input file. Exit." << endl;
		assert(false);
	}

	if (!fout.is_open()) {
		cerr << "Unable to write to output file. Exit." << endl;
		assert(false);
	}

	while (fin.good()) {
		// read next example
		getline(fin, line);
		if (line.empty() || line[0] == '#') // empty line or comment
			continue;

		// parse input
		parse_line(line, instance_vector);

		// make prediction
		pair<int, double> prediction = classify(instance_vector);
		y_hat = prediction.first;
		confidence = prediction.second;

		if (instance_vector.y != 0) {
			correct += (y_hat == instance_vector.y) ? 1 : 0;
		}
		total += 1;
		// map to label and output
		if (input_format == 1 || input_format == 3) {
			label = klass_rindex[y_hat];
			fout << label;
		} else if (input_format == 2) {
			fout << y_hat;
		} else {
			cerr << "Error: unknown input format: " << input_format << endl;
			assert(false);
		}
		if (detailed_output)
			fout << " " << confidence;
		fout << endl;
	}

	// print accuracy
	cout << "Accuracy : " << (float) correct / (float) total << " (" << correct
			<< "/" << total << ")" << endl;

	// clean up
	fin.close();
	fout.close();

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

	// read dimension
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
		// read klass index (for two classesm that's why it is repeated)
		// klass one
		fin >> token;
		fin >> id;
		klass_index[token] = id;
		klass_rindex[id] = token;
		// klass two
		fin >> token;
		fin >> id;
		klass_index[token] = id;
		klass_rindex[id] = token;

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
	for (size_t i = 0; i < N; i++) {
		fin >> v;
		u.push_back(v);
	}

	// clean up
	fin.close();

	return 0;
}

int main(int argc, char **argv) {
	char c;
	char inputfname[1024], modelfname[1024], outputfname[1024];

	while ((c = getopt(argc, argv, "dh")) != -1) {
		switch (c) {
		case 'd':
			detailed_output = true;
			break;
		case 'h':
			print_usage();
			return (0);
		default:
			print_usage();
			return -1;
		}
	}

	if (argc - optind != 3) {
		print_usage();
		return -1;
	}
	strcpy(inputfname, argv[optind++]);
	strcpy(modelfname, argv[optind++]);
	strcpy(outputfname, argv[optind++]);

	cerr << "Input file   : " << inputfname << endl;
	cerr << "Model file   : " << modelfname << endl;
	cerr << "Output file  : " << outputfname << endl;

	// load model
	load_model(modelfname);

	// classify
	test(inputfname, outputfname);

	return 0;
}
