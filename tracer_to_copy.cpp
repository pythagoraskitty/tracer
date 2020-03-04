
// DEBUG ----->
#include <fstream>
#include "base/debug/stack_trace.h"
// <----- DEBUG


// DEBUG ----->
std::string filepath("../trace/output.txt");
std::ofstream outfile;
outfile.open(filepath, std::fstream::app);
if (!outfile.is_open())
  LOG(ERROR) << "file not opened: try running with --no-sandbox";
outfile << "*****" << std::endl;
outfile << base::debug::StackTrace().ToString();
outfile.close();
// <----- DEBUG
