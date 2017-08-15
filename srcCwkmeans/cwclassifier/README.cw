09-May-2012

This README file describes the Confidence Weighted Learning (CW)
online learning algorithms for linear classification.
Copyright (C) 2012 Daniel Dahlmeier and Hwee Tou Ng


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


If you are using the CW learning algorithm in your work, please
include a citation of the following paper:

Daniel Dahlmeier, Hwee Tou Ng, and Eric Jun Feng Ng. 2012. NUS at the
HOO 2012 Shared Task. In Proceedings of the Seventh Workshop on
Innovative Use of NLP for Building Educational Applications

Any questions regarding the CW learning algorithm should be directed
to Daniel Dahlmeier(danielhe@comp.nus.edu.sg).



Contents
========
0. Quickstart
1. Installation
2. Running the classifiers 
3. References




0. Quickstart
=============
Unpack and build:
$ tar xfvz cw-release.tar.gz
$ make

The executable files will be in the bin/ directory.




1. Installation 
================

make
 


2. Running the classifiers 
============================


2.1 Data format
---------------
Either raw features where each token is one atomic feature or libsvm format
For binary classification, the labels are -1 and +1
For multiclass classification, the labels are positive integers
1,2,3,..




2.2 Usage
---------

Train a binary classifier:
$ cw_binary_learn [OPTIONS] input model

Test a binary classifier:
$ cw_binary_classify [OPTIONS] input model output



Train a multiclass classifier:
$ cw_multiclass_learn [OPTIONS] input model  

Test a multiclass classifier:
$ cw_multiclass_classify [OPTIONS] input model output





3. References
=============
Confidence-Weighted Linear Classification 
Mark Dredze, Koby Crammer and Fernando Pereira 
Proceedings of the 25th International Conference on Machine Learning
(ICML), 2008 

Multi-Class Confidence Weighted Algorithms
Koby Crammer, Mark Dredze and  Alex Kulesza
Empirical Methods in Natural Language Processing (EMNLP), 2009
