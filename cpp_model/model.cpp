// Binary Brier score evaluation
// Repository: https://github.com/tltmgnt/TruthAI-Uncertainty-and-Calibration
// Standalone C++17, offline, synthetic reference model.
// Build: c++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp_model/model.cpp -o model
// Run: ./model    (runs built-in assertions and prints a bounded demo result)
// Research-only: no trained AI, independent validation, external actions or approval.
#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
#include <numeric>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

void require(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
namespace model {
double brier(const std::vector<double>&p,const std::vector<int>&y){if(p.empty()||p.size()!=y.size())throw std::invalid_argument("length");double sum=0;for(size_t i=0;i<p.size();++i){if(!std::isfinite(p[i])||p[i]<0||p[i]>1||(y[i]!=0&&y[i]!=1))throw std::invalid_argument("probability or label");double e=p[i]-y[i];sum+=e*e;}return sum/p.size();}
void demo(){double score=brier({.9,.2,.6},{1,0,1});require(std::abs(score-.07)<1e-10,"Brier sample");std::cout<<"synthetic_brier="<<score<<" population_calibration_validated=0";}
} // namespace model
int main(){try{std::cout<<std::boolalpha;model::demo();std::cout<<'\n';return 0;}catch(const std::exception&e){std::cerr<<"model test failed: "<<e.what()<<'\n';return 1;}}
