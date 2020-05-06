
// DEBUG ----->
#include <fstream>
#include <sstream>
#include "base/debug/stack_trace.h"
// <----- DEBUG

// DEBUG ----->
#define tr(...) trace(#__VA_ARGS__, __VA_ARGS__)
#define trstr(...) trace(#__VA_ARGS__, __VA_ARGS__).str()

template <typename Arg1>
std::basic_stringstream<char> trace(const char* name, Arg1&& arg1) {
  std::basic_stringstream<char> out;
  out << name << " : " << arg1 << " ";
  return out;
}

template <typename Arg1, typename... Args>
std::basic_stringstream<char> trace(const char* names,
                                        Arg1&& arg1,
                                        Args&&... args) {
  std::basic_stringstream<char> out;
  const char* comma = strchr(names + 1, ',');
  out.write(names, comma - names);
  out << " : " << arg1 << " | ";
  out << trace(comma + 1, args...).str();
  return out;
}

// <----- DEBUG


// DEBUG ----->
std::string filepath("../trace/output.txt");
std::ofstream outfile;
outfile.open(filepath, std::fstream::app);
if (!outfile.is_open())
  LOG(ERROR) << "file not opened: try running with --no-sandbox";
outfile << "*****" << trstr(args) << "*****" << std::endl;
outfile << base::debug::StackTrace().ToString();
outfile.close();
// <----- DEBUG
