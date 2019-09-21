from collections import defaultdict
import copy

class Node:

    def __init__(self, value, father):
        self.value = value
        self.children = []
        self.father = father

class nAryTree(object):

    def __init__(self, data):
        self.root = Node(data, None)

    def getRoot(self):
        return self.root

    def insert(self, currentNode, data):
        if not data:
            return
        if not currentNode:
            return
        newNode = Node(data, currentNode)
        currentNode.children.append(newNode)
        print("Padre: " + currentNode.value + " | Hijo: " + data)
        return newNode


def make_expression(ast):
    """
    This function receives a sequence (list or tuple) representing the abstract syntax tree of a logical expression and returns an expression object suitable for further processing.
    
    In the Abstract Syntax Tree, the first element of the sequence is the operator (if applicable), with the subsequent items being the arguments to that operatior. The possible operators are:
    
       - "and" with *arbitrarily many parameters*
       - "or" with *arbitrarily many parameters*
       - "not" with exactly one parameter 
       - "=" with exactly two parameters which are variables or constants
       - "imply" with exactly two parameters 
       - "when" with exactly two parameters 
       - "exists" with exactly two parameters, where the first one is a variable specification
       - "forall" with exactly two parameters, where the first one is a variable specification
    
    Unless otherwise noted parameters may be, in turn, arbitrary expressions. Variable specifications are sequences of one or three elements:
       - A variable specification of the form ("?s", "-", "Stories") refers to a variable with name "?s", which is an element of the set "Stories"
       - A variable specification of the form ("?s",) refers to a variable with name "?s" with no type 
       
    If the first element of the passed sequence is not a parameter name, it can be assumed to be the name of a predicate in an atomic expression. In this case, 
    the remaining elements are the parameters, which may be constants or variables.
    
    An example for an abstract syntax tree corresponding to the expression 
          "forall s in stories: (murdermystery(s) imply (at(sherlock, bakerstreet) and not at(watson, bakerstreet) and at(body, crimescene)))" 
    would be (formatted for readability):
    
        ("forall", ("?s", "-", "Stories"), 
                   ("imply", 
                         ("murdermystery", "?s"),
                         ("and", 
                              ("at", "sherlock", "bakerstreet"),
                              ("not", 
                                   ("at", "watson", "bakerstreet")
                              ),
                              ("at", "body", "crimescene")
                         )
                   )
        )
    
    The return value of this function can be an arbitrary python object representing the expression, which will later be passed to the functions listed below. For notes on the "when" operator, 
    please refer to the documentation of the function "apply" below. Hint: A good way to represent logical formulas is to use objects that mirror the abstract syntax tree, e.g. an "And" object with 
    a "children" member, that then performs the operations described below.
    """

    if isinstance(ast[0], tuple):
        print('Invalid Start of Expression')
        return None
    #Set the root
    expressionTree = nAryTree(ast[0])
    print("Root: " + expressionTree.getRoot().value)
    #Start for each element of the root operator
    for x in ast[1:]:
        recursiveAnalisys(expressionTree, expressionTree.getRoot(), x)

    #searchInTree(expressionTree.getRoot(), "a")

    return expressionTree

def recursiveAnalisys(tree, currentNode, data):
    if not isinstance(data, tuple):
        if data == "-":
            return
        tree.insert(currentNode, data)
        return

    newCurrentNode = tree.insert(currentNode, data[0])
    for x in data[1:]:
        recursiveAnalisys(tree, newCurrentNode, x)

    return
    
def searchInTree(startNode, key):
    result = []                   
    if startNode.value == key:
        print ('found: ' + startNode.value)
        result.append(startNode)   
    else:
        print ('Searching in: ' + startNode.value)
    for subtree in startNode.children:         
        result.extend(searchInTree(subtree, key)) 

    return result

def make_world(atoms, sets):
    """
    This function receives a list of atomic propositions, and a dictionary of sets and returns an object representing a logical world.
    
    The format of atoms passed to this function is identical to the atomic expressions passed to make_expression above, i.e. 
    the first element specifies the name of the predicate and the remaining elements are the parameters. For example 
       ("on", "a", "b") represents the atom "at(a, b)"
       
    The sets are passed as a dictionary, with the keys defining the names of all available sets, each mapping to a sequence of strings. 
    For example: {"people": ["holmes", "watson", "moriarty", "adler"], 
                  "stories": ["signoffour", "scandalinbohemia"], 
                  "": ["holmes", "watson", "moriarty", "adler", "signoffour", "scandalinbohemia"]}
                  
    The entry with the key "" contains all possible constants, and can be used if a variable is not given any particular domain.
    
    The world has to store these sets in order to allow the quantifiers forall and exists to use them. When evaluated, the forall operator from the 
    example above would look up the set "stories" in the world, and use the values found within to expand the formula.
    
    Similar to make_expression, this function returns an arbitrary python object that will only be used to pass to the functions below. Hint: It may be beneficial 
    to store the atoms in a set using the same representation as for atomic expressions, and the set dictioary as-is.
    """

    #Creating the default dictionary
    world = defaultdict(list)
    numKeys = 0

    #Adding to the default dictionary each set
    for item in sets.items():
        keyName = ""
        for key in item:
            
            if numKeys%2 == 0:
                keyName = key
            else:
                for value in key:
                    world[keyName].append(value)
            numKeys = numKeys + 1

    #Adding to the default dictionary each atom as a tuple to a key
    for tuples in atoms:
        tuple = [tuples[1], tuples[2]]
        world[tuples[0]].append(tuple)

    #print (world)

    return world
    
def models(world, condition):
    """
    This function takes a world and a logical expression, and determines if the expression holds in the given world, i.e. if the world models the condition.
    
    The semantics of the logical operators are the usual ones, i.e. a world models an "and" expression if it models every child of the "and" expression, etc.
    For the quantifiers, when the world is constructed it is passed all possible sets, and the quantifiers will use this dictionary to determine their domain. 
    
    The special "when" operator is only used by the "apply" function (see below), and no world models it.
    
    The return value of this function should be True if the condition holds in the given world, and False otherwise.
    """
    result = checkTree(world, condition.getRoot(), condition)

    return result    

def checkTree(world, currentNode, tree):

    if currentNode.value == "and":
        for subtree in currentNode.children:
            if not checkTree(world, subtree, tree):
                print("AND: False")
                return False
        print("AND: True")
        return True
    elif currentNode.value == "or":
        for subtree in currentNode.children:
            if checkTree(world, subtree, tree):
                print("OR: True")
                return True
        print("OR: False")
        return False
    elif currentNode.value == "not":
        print("NOT: ", end="")
        return not checkTree(world, currentNode.children[0], tree)
    elif currentNode.value == "=":
        for subtree in currentNode.children:
            checkTree(world, subtree, tree)
        print("Evaluating =")
    elif currentNode.value == "imply":
        if not checkTree(world, currentNode.children[0], tree):
            print("IMPLY: True")
            return True
        elif checkTree(world, currentNode.children[1], tree):
            print("IMPLY: True")
            return True
        print("IMPLY: False")
        return False
    elif currentNode.value == "when":
        for subtree in currentNode.children:
            checkTree(world, subtree, tree)
        print("Evaluating when")
    elif currentNode.value == "exists":
        for subtree in currentNode.children:
            checkTree(world, subtree, tree)
        print("Evaluating exists")
    elif currentNode.value == "forall":
        #for values in world[currentNode.children[0].children[0].value]:
            #newTree = substituteFromSubTree(tree, currentNode.children[0].value, values)
            #if not checkTree(world, subtree, newTree)

        print(currentNode.children[0].value)
        print(currentNode.children[0].children[0].value)
    else:
        print(currentNode.value + ": ", end="")
        if len(world[currentNode.value]) > 0:
            for tuple in world[currentNode.value]:
                if tuple[0] == currentNode.children[0].value and tuple[1] == currentNode.children[1].value:
                    print(tuple[0] + "/" + currentNode.children[0].value + " and " + tuple[1] + "/" + currentNode.children[1].value + " --- TRUE")
                    return True
            print(tuple[0] + "/" + currentNode.children[0].value + " and " + tuple[1] + "/" + currentNode.children[1].value + " --- False")
            return False
        else:
            return False
    return False

def checkInWorld(startNode, key):
    result = []                   
    if startNode.value == key:
        print ('found: ' + startNode.value)
        result.append(startNode)   
    else:
        print ('Searching in: ' + startNode.value)
    for subtree in startNode.children:         
        result.extend(searchInTree(subtree, key)) 

    return result
    
def substitute(expression, variable, value):
    """
    This function takes an expression, the name of a variable (usually starting with a question mark), and a constant value, and returns a *new* expression with all occurences of the variable 
    replaced with the value
    
    Do *not* replace the variable in-place, always return a new expression object. When you implement the quantifiers, you should use this same functionality to expand the formula to all possible 
    replacements for the variable that is quantified over.
    """
    newTree = copy.deepcopy(expression)

    replaceInTree(newTree.getRoot(), variable, value)

    return newTree

def replaceInTree(currentNode, key, newValue):                
    if currentNode.value == key:
        currentNode.value = newValue
        print ('Replacing: ' + key + ' to ' + currentNode.value)

    for subtree in currentNode.children:         
        replaceInTree(subtree, key, newValue) 

    return 
    
    
def apply(world, effect):
    """
    This function takes a world, and an expression, and returns a new world, with the expression used to change the world. 
    
    For the effect you can assume the following restrictions:
       - The basic structure of the effect is a conjunction ("and") of modifications.
       - Each modification may be a literal (atom, or negation of an atom), a forall expression, or a when expression 
       - In the world produced by the application, positive literals should be added to the atoms of the world, and negative literals should be removed 
       - Forall expressions should be expanded by substituting the variable and processed recursively in the same way (the inner expression will only contain a conjunction of 
             literals, forall expressions, and when expressions as well)
       - "when" expressions have two parameters: A condition (which may be an arbitrary expression), and an effect, which follows the same restrictions (conjunction of literals, forall expressions and when expressions)
             The way "when" expressions are applied to a world depends on the condition: If the world models the condition (i.e. models(world, condition) is true, the effect is applied to the world. Otherwise, nothing happens.
             "when" expressions provide a nice, succinct way to define conditional effects, e.g. if someone is trying to open a door, the door will only open if it is unlocked.
             
    If an effect would cause the same atom to be set to true and to false, it should be set to false, i.e. removed from the set.
             
    The result of this function should be a *new* world, with the changes defined by the effect applied to the atoms, but with the same definition of sets as the original world. 
    
    Hint: If your world stores the atoms in a set, you can determine the change of the effect as two sets: an add set and a delete set, and get the atoms for the new world using basic set operations.
    """
    print ("world before effect: ")
    print (world)
    world = applyToWorld(world, effect.getRoot())
    print ("world after effect: ")
    print (world)
    return world

def applyToWorld(world, currentNode):
    if currentNode.value == "and":
        print("Applying and")
        for subtree in currentNode.children:
            applyToWorld(world, subtree)
    elif currentNode.value == "not":
        print("Applying not")
        if len(world[currentNode.children[0].value]) > 0:
            try:
                world[currentNode.children[0].value].remove([currentNode.children[0].children[0].value, currentNode.children[0].children[1].value])
            except Exception as error:
                print (error)
            print("popped")
            return world
        else:
            return world
    elif currentNode.value == "=":
        for subtree in currentNode.children:
            checkTree(world, subtree)
        print("Applying =")
    elif currentNode.value == "imply":
        for subtree in currentNode.children:
            checkTree(world, subtree)
        print("Applying imply")
    elif currentNode.value == "when":
        for subtree in currentNode.children:
            checkTree(world, subtree)
        print("Applying when")
    elif currentNode.value == "exists":
        for subtree in currentNode.children:
            checkTree(world, subtree)
        print("Applying exists")
    elif currentNode.value == "forall":
        for subtree in currentNode.children:
            checkTree(world, subtree)
        print("Applying forall")
    else:
        print("Applying " + currentNode.value)
        print("Adding " + currentNode.value + ": " + "[" + currentNode.children[0].value + "," + currentNode.children[0].value + "]")
        world[currentNode.value].append([currentNode.children[0].value, currentNode.children[1].value])
        return world
    return world


if __name__ == "__main__":
    exp = make_expression(("or", ("on", "a", "b"), ("on", "a", "d")))
    world = make_world([("on", "a", "b"), ("on", "b", "c"), ("on", "c", "d")], {})
    substitute(exp, "a", "z")
    
    print(models(world, exp))
    print("Should be True: ", end="")

    print("---------------------------------------------------------------------")

    change = make_expression(["and", ("not", ("on", "a", "b")), ("on", "a", "c")])
    
    
    print(models(apply(world, change), exp))
    print("Should be False: ", end="")

    print("---------------------------------------------------------------------")
    
    print("mickey/minny example")
    world = make_world([("at", "store", "mickey"), ("at", "airport", "minny")], {"Locations": ["home", "park", "store", "airport", "theater"], "": ["home", "park", "store", "airport", "theater", "mickey", "minny"]})
    exp = make_expression(("and", 
        ("not", ("at", "park", "mickey")), 
        ("or", 
              ("at", "home", "mickey"), 
              ("at", "store", "mickey"), 
              ("at", "theater", "mickey"), 
              ("at", "airport", "mickey")), 
        ("imply", 
                  ("friends", "mickey", "minny"), 
                  ("forall", 
                            ("?l", "-", "Locations"),
                            ("imply",
                                    ("at", "?l", "mickey"),
                                    ("at", "?l", "minny"))))))
                                    
    print(models(world, exp))
    print("Should be True: ", end="")

    print("---------------------------------------------------------------------")
    
    become_friends = make_expression(("friends", "mickey", "minny"))
    friendsworld = apply(world, become_friends)
    
    print(models(friendsworld, exp))
    print("Should be False: ", end="")
    print("---------------------------------------------------------------------")

    '''
    move_minny = make_expression(("and", ("at", "store", "minny"), ("not", ("at", "airport", "minny"))))
    
    movedworld = apply(friendsworld, move_minny)
    print("Should be True: ", end="")
    print(models(movedworld, exp))
    
    
    move_both_cond = make_expression(("and", 
                                           ("at", "home", "mickey"), 
                                           ("not", ("at", "store", "mickey")), 
                                           ("when", 
                                                 ("at", "store", "minny"), 
                                                 ("and", 
                                                      ("at", "home", "minny"), 
                                                      ("not", ("at", "store", "minny"))))))
                                                      
    
    print("Should be True: ", end="")
    print(models(apply(movedworld, move_both_cond), exp))
    
    print("Should be False: ", end="")
    print(models(apply(friendsworld, move_both_cond), exp))
    
    exp1 = make_expression(("forall", 
                            ("?l", "-", "Locations"),
                            ("forall",
                                  ("?l1", "-", "Locations"),
                                  ("imply", 
                                       ("and", ("at", "?l", "mickey"),
                                               ("at", "?l1", "minny")),
                                       ("=", "?l", "?l1")))))
                                       
    print("Should be True: ", end="")
    print(models(apply(movedworld, move_both_cond), exp1))
    
    print("Should be False: ", end="")
    print(models(apply(friendsworld, move_both_cond), exp1))
    '''