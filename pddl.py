import sys
import expressions
import re

def readDocument (fname):
    with open(fname, 'r') as file:
        data = file.read().lower()
    data = list(filter(None, re.split('\s+;.*|([()])|\s+', data, flags=re.M)))
    #print(data)
    #print('---------------------------------------------------------------------')
    return data

def parse_domain(fname):
    """
    Parses a PDDL domain file contained in the file fname
    
    The return value of this function is passed to planner.plan, and does not have to follow any particular format
    """

    #------------------------------------------------------------------------- Tokenize/Regex
    dataD = readDocument(fname)
    #------------------------------------------------------------------------- Abstract Tree

    #abstractSyntaxTree = {'name' : '', 'requirements': [], 'types' : [], 'constants' : [], 'predicates' : [], 'actions' : {'name' : '', 'parameters' : [], 'precondition': [], 'effect' : []}}
    temporalList = []
    abstractSyntaxTree= []
    isAction = False

    for element in dataD:
        #print(element)
        temporalList.append(element)
        if element == ':action':
            isAction = True
        if element == ')':
            popping = True
            temporalList.pop()
            abstractSyntaxTree.append([])
            while popping:
                if temporalList[-1] == '(':
                    popping = False
                    temporalList.pop()
                    temporalList.append(list(reversed(abstractSyntaxTree.pop())))
                else:
                    abstractSyntaxTree[-1].append(temporalList.pop())
    #print('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-')
    abstractSyntaxTree = temporalList
    #print(abstractSyntaxTree)
    #print('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-')


    #------------------------------------------------------------------------- Identifying Parts

    typesDictionary = {}
    predicatesDictionary = {}
    actionsDictionary = {}
    temporalAction = []
    actionsIndex = 0
    acceptedPDDL = True
    indexTree = -1
 
    for element in abstractSyntaxTree[0]:
        #print (element)
        indexTree = indexTree + 1

        if type(element) is list:
            item = element[0]
        else:
            continue

        if item == 'domain':
            print('---------------------------------------  DOMAIN  ---------------------------------------')
            print('Name: ', end='')
            print(element.pop())

        elif item == ':requirements':
            print('----  Requirements  ----')
            #print(element)
            for req in element: 
                if not (req == ':requirements' or req == ':strips' or req == ':typing' or req == ':disjunctive-preconditions' or req == ':equality' or req == ':existential-preconditions' or req == ':universal-preconditions' or req == ':conditional-effects' or req == ':adl'):
                    acceptedPDDL = False
            if acceptedPDDL:
                print('Accepted PPDL file.')
            else:
                print('Invalid PDDL file.')
            
        elif item == ':types':
            for keys in element:
                if keys in typesDictionary or keys == ':types':
                    continue
                typesDictionary[keys] = set() 
            #print('----Types dictionary----')
            #print(typesDictionary)

        elif item == ':constants':
            constants = []
            typesDictionary[''] = set()
            settingKey = False

            for currentConstant in element:
                if currentConstant == '-':
                    settingKey = True
                elif currentConstant == ':constants':
                    continue
                elif settingKey:
                    typesDictionary[currentConstant] = set() 
                    setDic = typesDictionary[currentConstant]
                    while len(constants) > 0:
                        c = constants.pop()
                        setDic.add(c)
                        typesDictionary[''].add(c)
                    settingKey = False
                else:
                    constants.append(currentConstant)
            #print('--------Constants-------')
            #print(typesDictionary)

        elif item == ':predicates':
            #print(actionsDictionary.keys())
            print('----   Predicates   ----')
            #Optional
            print('Not Yet')
        elif item == ':action':
            #Creates a new key/set in the dictionary [[Name, [parameters], [preconditions], [effects]], [...], ...]
            actionsDictionary[element[1]] = [[],[],[]]
            actDic = actionsDictionary[element[1]]
            #print(element)
            actionName = element[1]
            for i in range(len(element)):
                
                #if element[i] == ':action':
                    #print('----------Action----------')
                    #print(actionName)

                if element[i] == ':parameters':
                    #print('----------Parameters----------')
                    i += 1
                    #print(element[i])
                    currentKey = ''
                    actDic[actionsIndex] = {}
                    actDic[actionsIndex][currentKey] = set()
                    #actDic[actionsIndex][currentKey] = set(
                    for e in (list(reversed(element[i]))):
                       # print(e)
                        if e.startswith('?'):
                            actDic[actionsIndex][currentKey].add(e)
                        elif e == '-':
                            continue
                        else:
                            currentKey = e
                            if currentKey in actDic[actionsIndex]:
                                continue
                            else:
                                actDic[actionsIndex][currentKey] = set()
                

                elif element[i] == ':precondition':
                    #print('----------Preconditions----------')
                    i += 1
                    actDic[1] = listToTuple(element[i])
                    #print(actDic[1])
                    #print('---------------------------------')

                elif element[i] == ':effect':
                    #print('----------Effect----------')
                    i += 1
                    actDic[2] = listToTuple(element[i])
                    #print(actDic[2])
                    #print('---------------------------------')

    return [actionsDictionary, typesDictionary] 
    
def parse_problem(fname):
    """
    Parses a PDDL problem file contained in the file fname
    
    The return value of this function is passed to planner.plan, and does not have to follow any particular format
    """

        #------------------------------------------------------------------------- Tokenize/Regex
    dataP = readDocument(fname)

    #------------------------------------------------------------------------- Abstract Tree

    abstractSyntaxTreeP = []
    temporalList = []
    pushing = True
    for element in dataP:
        #print(element)
        temporalList.append(element)
        if element == ':action':
            isAction = True
        if element == ')':
            popping = True
            temporalList.pop()
            abstractSyntaxTreeP.append([])
            while popping:
                if temporalList[-1] == '(':
                    popping = False
                    temporalList.pop()
                    temporalList.append(list(reversed(abstractSyntaxTreeP.pop())))
                else:
                    abstractSyntaxTreeP[-1].append(temporalList.pop())
    abstractSyntaxTreeP = temporalList
    #print(abstractSyntaxTreeP)
    #------------------------------------------------------------------------- Identifying Parts
    
    typesDictionary = {}
    initialStates = []
    rawGoals = []
    indexTree = 0

    for element in abstractSyntaxTreeP[0]:
        #print (element)
        indexTree = indexTree + 1

        if type(element) is list:
            item = element[0]
        else:
            continue
        #print(item)

        if item == 'problem':
            print('---------------------------------------  PROBLEM  ---------------------------------------')
            print('Name: ', end='')
            print(element[1])
            ('-----------------------------------------------------------------------------------------')
        elif item == ':init':
            #print('----------------------Initial States----------------------')
            for i in element:
                if i != ':init':
                        initialStates.append(tuple(i))
            #print(initialStates)

        elif item == ':goal':
            #print('---------------------------Goals---------------------------')
            for i in element:
                if i != ':goal':
                    rawGoals.append(i)
            rawGoals = listToTuple(rawGoals)
            #print(rawGoals)

        elif item == ':objects':
            #print('----------------------Objects----------------------')
            setObjects(element, typesDictionary)

    #expressionGoal = expressions.make_expression(list(reversed(rawGoals)))
    #printNAryTree(expressionGoal.getRoot())

    return [typesDictionary, initialStates, rawGoals]

def printNAryTree(node):
    for child in node.children:
        print('Father: ', end='')
        print(child.father.value)
        print('Child: ', end='')
        print(child.value)
        print('')
        printNAryTree(child)
        
def listToTuple(exp):
    tupleExp = []
    recursive = False
    for i in range(len(exp)):
        if type(exp[i]) == list:
            exp[i] = tuple(listToTuple(exp[i])) 
            recursive = True
    tupleExp = exp
    return tupleExp

def setObjects(element, typesDictionary):
    #print('----------------------Objects----------------------')
    constants = []
    typesDictionary[''] = set()
    settingKey = False

    for currentConstant in element:
        if currentConstant == '-':
            settingKey = True
        elif currentConstant == ':objects':
            continue                    
        elif settingKey:
            typesDictionary[currentConstant] = set() 
            setDic = typesDictionary[currentConstant]
            while len(constants) > 0:
                c = constants.pop()
                setDic.add(c)
                typesDictionary[''].add(c)
            settingKey = False
        else:
            constants.append(currentConstant)
    #print(typesDictionary)
    
if __name__ == "__main__":
    parse_domain(sys.argv[1])
    parse_problem(sys.argv[2])