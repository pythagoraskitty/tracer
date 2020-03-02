
// DEBUG ----->
#include <fstream>
#include "base/debug/stack_trace.h"
// <----- DEBUG


// DEBUG ----->
std::string filepath("output.txt");
std::ofstream outfile;
outfile.open(filepath, std::fstream::app);
outfile << "*****" << std::endl;
outfile << base::debug::StackTrace().ToString();
outfile.close();
// <----- DEBUG
