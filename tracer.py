  paren = stacktrace.find("()", position + 1)
  if paren == -1:
    return -1
  colons = stacktrace.rfind("::", 0, paren - 1)
  if colons == -1:
    raise ValueError(":: not found")
  return colons

def GetNextMethod(stacktrace, position):
  paren = stacktrace.find("()", position + 1)
  if paren == -1:
    # no more methods
    return ""
  colons = stacktrace.rfind("::", 0, paren - 1)
  if colons == -1:
    raise ValueError(":: not found")
  start = colons + len("::")
  return stacktrace[start : paren + len("()")]

def GetNextObject(stacktrace, position, namespace_filter = set()):
  end_colons = GetNextObjMethodSeparator(stacktrace, position)
  if end_colons == -1:
    return ""
  space = stacktrace.rfind(" ", 0, end_colons - 1)
  if space == -1:
    raise ValueError("no space found")
  start = space + 1
  colons = stacktrace.find("::", start + 1)
  if colons == -1:
    raise ValueError(":: not found")
  while colons != end_colons and stacktrace[start : colons] in namespace_filter:
    # TODO skip (anonymous namespace)
    start = colons + len("::")
    colons = stacktrace.find("::", colons + 1)
    if colons == -1:
      raise ValueError(":: not found")
  return stacktrace[start : end_colons]

def IsAtLeafMethod(stacktrace, position, leaf_methods = set()):
  method = GetNextMethod(stacktrace, position)
  # ok to leave off parentheses in set of leaf methods
  return method in leaf_methods or method[:-2] in leaf_methods

def AdvancePosition(stacktrace, position):
  return stacktrace.find("#", position + 1)

def GetPositionAfterDebugObjects(stacktrace):
  if len(stacktrace) < len("base::debug::"):
    return -1
  position = stacktrace.rfind("base::debug::")
  if position == -1:
    return -1
  return AdvancePosition(stacktrace, position)

def GetObjectStack(stacktrace, namespace_filter = set(), leaf_methods = set()):
  stack = []
  position = GetPositionAfterDebugObjects(stacktrace)
  if position == -1:
    return []
  class_object = GetNextObject(stacktrace, position, namespace_filter)
  method = GetNextMethod(stacktrace, position)
  while class_object != "" and method != "" and not IsAtLeafMethod(stacktrace, position, leaf_methods):
    if len(stack) == 0 or class_object != stack[-1]:
      stack.append(class_object)
    class_object = GetNextObject(stacktrace, position, namespace_filter)
    method = GetNextMethod(stacktrace, position)
    position = AdvancePosition(stacktrace, position)
  return stack

def GetStacktraces(trace_file_path, separator_string):
  traces = []
  with open(trace_file_path, "r") as input_file:
    data = input_file.read()
    position = data.find(separator_string)
    while position != -1:
      previous = position + len(separator_string)
      position = data.find(separator_string, previous)
      traces.append(data[previous : position])
    # last string appended had erroneous right endpoint of -1
    traces.pop()
    traces.append(data[previous :])
  return traces

class TrieNode:
  def __init__(self, name):
    self.name = name
    self.children = dict()
    self.parent = None
    self.count = 0

  def AppendChild(self, child_name):
    if not child_name in self.children:
      self.children[child_name] = TrieNode(child_name)
      self.children[child_name].parent = self

  def Print(self):
    if self.parent != None:
      print(self.parent.name, end = "")
    else:
      print("\t", end = "")
    print("::", self.name, self.count, "-<", end = "")
    if len(self.children) == 0:
      print(">")
      return
    for child_name in self.children:
      print(child_name, "+ ", end = "")
    print(">")
    for child_name in self.children:
      node = self.children[child_name]
      node.Print()

class Trie:
  # TODO should I let this be a graph with cycles rather than strictly a trie?
  def __init__(self, root):
    self.root = TrieNode(root)
    self.descendants = set()
    if self.root != None:
      self.descendants.add(self.root.name)

  def HasPath(self, path):
    if len(path) == 0 or path[0] != self.root.name:
      return False
    index = 1
    node = self.root
    while index < len(path):
      if not path[index] in node.children:
        return False
      node = node.children[path[index]]
      index += 1
    return True

  def InsertPath(self, path):
    if len(path) == 0 or path[0] != self.root.name:
      return False
    index = 1
    node = self.root
    node.count += 1
    while index < len(path):
      if not path[index] in node.children:
        node.AppendChild(path[index])
        self.descendants.add(path[index])
      node = node.children[path[index]]
      node.count += 1
      index += 1
    return True

  def Print(self):
    if type(self.root) == type("string"):
      print(self.root)
    else:
      self.root.Print()
    print("descendants:", self.descendants)

def BuildTries(trace_file_path, separator_string, namespace_filter = set(), leaf_methods = set()):
  traces = GetStacktraces(trace_file_path, separator_string)
  stacks = [GetObjectStack(stacktrace, namespace_filter, leaf_methods) for stacktrace in traces]
  stack_map = dict()
  for stack in stacks:
    if len(stack) == 0:
      continue

    if not stack[0] in stack_map:
      stack_map[stack[0]] = []
    stack_map[stack[0]].append(stack)

  tries = [Trie(root) for root in stack_map]
  for trie in tries:
    stack_list = stack_map[trie.root.name]
    for stack in stack_list:
      trie.InsertPath(stack)

  return tries





##########

tries = BuildTries("extrace.txt", "***", {"blink", "content", "base", "v8", "internal"}, {"Run", "Accept", "RunTask", "DoWorkImpl", "DoSomeWork"})

for trie in tries:
  print('\n' * 3)
  print("*****")
  trie.Print()

sets_to_check = { trie.root.name : trie.descendants for trie in tries}
print('\n' * 10)
print("*****")
print(sets_to_check)
