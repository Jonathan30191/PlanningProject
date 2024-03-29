import expressions
from copy import copy, deepcopy

class Node:
    def get_id(self):
        """
        Returns some unique identifier for the node (for example, the name, the hash value of the contents, etc.), used to compare two nodes for equality.
        """
        return ""
    def get_neighbors(self):
        """
        Returns all neighbors of a node, and how to reach them. The result is a list Edge objects, which contains 3 attributes target, cost and name, where target is a Node object, cost is a numeric value representing the distance between the two nodes, and name is a string representing the path taken to the neighbor.
        """
        return []
    def __eq__(self, other):
        return self.get_id() == other.get_id()

class PlanNode(Node):
    def __init__(self, nodeStates, domainTypes, problemTypes, world, name):
        self.name = name
        self.neighbors = []
        self.initialStates = nodeStates
        self.domainTypes = domainTypes
        if problemTypes != None:
            self.set_types(problemTypes)
        self.world = world

    def get_neighbors(self, allActions, actionDictionary, useheuristic):
        
        self.createNeighbors_PlanNode(allActions, actionDictionary, useheuristic)
        return self.neighbors

    def get_id(self):
        return self.name
    
    def set_types(self, problemTypes):
        allKeys = problemTypes.keys()

        for key in allKeys:
            if not key in self.domainTypes:
                self.domainTypes[''] = set()
                setDic = self.domainTypes[key]
            else:
                setDic = self.domainTypes[key]
            
            for value in problemTypes[key]:
                setDic.add(value)
        
                
    def set_initialStates(self):
        #print('++++++++++++++++++++++++++World++++++++++++++++++++++++++++++++++++++++')
        self.world = expressions.make_world(self.initialStates, self.domainTypes)
        #print(self.world)
        #print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    def set_possibleActions(self, actions):
        #Actions is a dictionary: {Name: [[parameters] [precondition] [effect]]}
        allActions = {}
        allActionsKeys = actions.keys()
        for k in allActionsKeys:
            #print('')
            #print('')
            #print('------------------------------------', end='')
            #print(k, end = '')
            #print('--------------------------------')
            allActions[k] = self.createPossibleActions(actions[k][0], actions[k][1])

        return allActions

    def createPossibleActions(self, parameters, precondition):
        #print('--------------------------------------------------------------------------------')
        #print('Parameters: ',end='')
        #print(parameters)
        #print('--------------------------------------------------------------------------------')
        #print('Precondition: ',end='')
        #print(precondition)
        #print('--------------------------------------------------------------------------------')
        #print('Dom Types: ',end='')
        #print(self.domainTypes)
        #print('--------------------------------------------------------------------------------')

        parameterKeys = parameters.keys()
        actionList = []
        singleAction = {}
        isFirst = True

        for key in parameterKeys:
            if len(parameters[key]) > 0:
                for toChange in parameters[key]:
                    if len(self.domainTypes[key]) > 0:
                        if isFirst:
                            isFirst = False
                            for item in self.domainTypes[key]:
                                singleAction[toChange] = item
                                actionList.append(singleAction.copy())
                        else:
                            retList = [] 
                            for action in actionList:
                                for item in self.domainTypes[key]:
                                    action[toChange] = item
                                    retList.append(action.copy())
                            actionList = retList.copy()
        #print('--------------------------------Possible Actions:', end='')
        #print(len(actionList), end = '')
        #print('--------------------------------')
        #for act in actionList:
        #    print(act)
        return actionList

    def createNeighbors_PlanNode(self, allPossibleActions, actionsDictionary, useheuristic):
        allKeys = allPossibleActions.keys()
        actionsKeys = actionsDictionary.keys()      
        #print('')
        #print(allPossibleActions)
        #print(actionsKeys)

        for key in allKeys:
            #print(key)
            #print(actionsDictionary[key][1])
            #print("--------------------------")
            #print(actionsDictionary[key][2])
            expTree = expressions.make_expression(actionsDictionary[key][1])

            if len(allPossibleActions[key]) < 1:
                neighName = ''
                neighName = '' + key + '()'
                precondition = []
                #print(neighName)
                if expressions.models(self.world, expTree):
                    #print('models')
                    tempworld = deepcopy(self.world)
                    if len(actionsDictionary[key][2]) == 1:
                        expEffect = actionsDictionary[key][2]
                        expressions.applyToWorld(tempworld, expEffect, useheuristic)
                        self.neighbors.append(Edge(PlanNode(self.initialStates, self.domainTypes, None, tempworld, neighName), 1, neighName))
                    else:
                        expEffect = expressions.make_expression(actionsDictionary[key][2])
                        for tuple in precondition:
                            expressions.substitute(expEffect, tuple[0], tuple[1])
                        expressions.applyToWorld(tempworld, expEffect, useheuristic)
                        self.neighbors.append(Edge(PlanNode(self.initialStates, self.domainTypes, None, tempworld, neighName), 1, neighName))
                #else:
                    #print(self.world)
                    #print('Does not models')

            else:
                for action in allPossibleActions[key]:
                
                    #print(actionsDictionary[key][1])
                    precondition = []
                    neighName = ''
                    neighName = '' + key + '('
                    first = True
                    second = True
                    allActionKeys = action.keys()
                    for ak in allActionKeys:
                        if first:
                            neighName = neighName + action[ak] + ', '
                            precondition.append((ak,action[ak]))
                            first = False
                        elif second:
                            neighName = neighName + action[ak]
                            precondition.append((ak,action[ak]))
                            second = False
                        else:
                            neighName = neighName+ ', ' + action[ak]
                            precondition.append((ak,action[ak]))
                    neighName = neighName + ')'

                    tempcopy = deepcopy(expTree)
                    for tuple in precondition:
                        expressions.substitute(tempcopy, tuple[0], tuple[1])
                
                    #print(neighName)
                    if expressions.models(self.world, tempcopy):
                        #print('')
                        #print(neighName)
                        #print(precondition)
                        #print(self.world)
                        tempworld = deepcopy(self.world)



                        #print('Applying: ')

                        if len(actionsDictionary[key][2]) == 1:
                            expEffect = actionsDictionary[key][2]
                            #print(tempworld)
                            expressions.applyToWorld(tempworld, expEffect, useheuristic)
                            #print(tempworld)
                            self.neighbors.append(Edge(PlanNode(self.initialStates, self.domainTypes, None, tempworld, neighName), 1, neighName))
                        else:
                            #print(tempworld)
                            expEffect = expressions.make_expression(actionsDictionary[key][2])
                            for tuple in precondition:
                                expressions.substitute(expEffect, tuple[0], tuple[1])
                            expressions.applyToWorld(tempworld, expEffect, useheuristic)
                            #print(tempworld)
                            self.neighbors.append(Edge(PlanNode(self.initialStates, self.domainTypes, None, tempworld, neighName), 1, neighName))
            #input("Press Enter to continue...")
                    #else:
                        #print('It does not models it.')

                    #altWorld = self.world.copy()
                    #altWorld = expressions.applyToWorld(altWorld, tempcopy.getRoot())
                    #print(self.world)
                #for item in self.neighbors:
                #    print(
                #    item.name)
                #print('---')

                



        
class Edge:
    """
    Abstraction of a graph edge. Has a target (Node that the edge leads to), a cost (numeric) and a name (string), which can be used to print the edge.
    """
    def __init__(self, target, cost, name):
        self.target = target 
        self.cost = cost
        self.name = name

class GeomNode(Node):
    """
    Representation of a finite graph in which all nodes are kept in memory at all times, and stored in the node's neighbors field.
    """
    def __init__(self, name):
        self.name = name
        self.neighbors = []
    def get_neighbors(self):
        return self.neighbors
    def get_id(self):
        return self.name
        
class InfNode(Node):
    """
    Infinite graph, in which every node represents an integer, and neighbors are generated on demand. Note that Nodes are not cached, i.e. if you
    request the neighbors of node 1, and the neighbors of node 3, both will contain the node 2, but they will be using two distinct objects. 
    """
    def __init__(self, nr):
        self.nr = nr
    def get_neighbors(self):
        result = [Edge(InfNode(self.nr-1),1,("%d - -1 - %d"%(self.nr,self.nr-1))), Edge(InfNode(self.nr+1),1,("%d - +1 - %d"%(self.nr,self.nr+1))), Edge(InfNode(self.nr*2),1,("%d - *2 - %d"%(self.nr,self.nr*2)))]
        if self.nr%2 == 0:
            result.append(Edge(InfNode(self.nr//2),1,("%d - /2 - %d"%(self.nr,self.nr//2))))
        return result
    def get_id(self):
        return self.nr


def make_geom_graph(cities, distances):
    result = {}
    for c in cities:
        result[c] = GeomNode(c)
    for (a,b,d) in distances:
        result[a].neighbors.append(Edge(result[b], d, "%s - %s"%(a,b)))
        result[b].neighbors.append(Edge(result[a], d, "%s - %s"%(b,a)))
    return result
    
Austria = make_geom_graph(
    ["Graz", "Vienna", "Salzburg", "Innsbruck", "Munich", "Bregenz", "Linz", "Eisenstadt", "Klagenfurt", "Lienz", "Bruck"],
    [("Graz", "Bruck", 55.0),
     ("Graz", "Klagenfurt", 136.0),
     ("Graz", "Vienna", 200.0),
     ("Graz", "Eisenstadt", 173.0),
     ("Bruck", "Klagenfurt", 152.0),
     ("Bruck", "Salzburg", 215.0),
     ("Bruck", "Linz", 195.0),
     ("Bruck", "Vienna", 150.0),
     ("Vienna", "Eisenstadt", 60.0),
     ("Vienna", "Linz", 184.0),
     ("Linz", "Salzburg", 123.0),
     ("Salzburg", "Munich", 145.0),
     ("Salzburg", "Klagenfurt", 223.0),
     ("Klagenfurt", "Lienz", 145.0),
     ("Lienz", "Innsbruck", 180.0),
     ("Munich", "Innsbruck", 151.0),
     ("Munich", "Bregenz", 180.0),
     ("Innsbruck", "Bregenz", 190.0)])
     
AustriaHeuristic = { 
   "Graz":       {"Graz": 0.0,   "Vienna": 180.0, "Eisenstadt": 150.0, "Bruck": 50.0,  "Linz": 225.0, "Salzburg": 250.0, "Klagenfurt": 125.0, "Lienz": 270.0, "Innsbruck": 435.0, "Munich": 375.0, "Bregenz": 450.0},
   "Vienna":     {"Graz": 180.0, "Vienna": 0.0,   "Eisenstadt": 50.0,  "Bruck": 126.0, "Linz": 175.0, "Salzburg": 285.0, "Klagenfurt": 295.0, "Lienz": 400.0, "Innsbruck": 525.0, "Munich": 407.0, "Bregenz": 593.0},
   "Eisenstadt": {"Graz": 150.0, "Vienna": 50.0,  "Eisenstadt": 0.0,   "Bruck": 171.0, "Linz": 221.0, "Salzburg": 328.0, "Klagenfurt": 335.0, "Lienz": 437.0, "Innsbruck": 569.0, "Munich": 446.0, "Bregenz": 630.0},
   "Bruck":      {"Graz": 50.0,  "Vienna": 126.0, "Eisenstadt": 171.0, "Bruck": 0.0,   "Linz": 175.0, "Salzburg": 201.0, "Klagenfurt": 146.0, "Lienz": 287.0, "Innsbruck": 479.0, "Munich": 339.0, "Bregenz": 521.0},
   "Linz":       {"Graz": 225.0, "Vienna": 175.0, "Eisenstadt": 221.0, "Bruck": 175.0, "Linz": 0.0,   "Salzburg": 117.0, "Klagenfurt": 311.0, "Lienz": 443.0, "Innsbruck": 378.0, "Munich": 265.0, "Bregenz": 456.0},
   "Salzburg":   {"Graz": 250.0, "Vienna": 285.0, "Eisenstadt": 328.0, "Bruck": 201.0, "Linz": 117.0, "Salzburg": 0.0,   "Klagenfurt": 201.0, "Lienz": 321.0, "Innsbruck": 265.0, "Munich": 132.0, "Bregenz": 301.0},
   "Klagenfurt": {"Graz": 125.0, "Vienna": 295.0, "Eisenstadt": 335.0, "Bruck": 146.0, "Linz": 311.0, "Salzburg": 201.0, "Klagenfurt": 0.0,   "Lienz": 132.0, "Innsbruck": 301.0, "Munich": 443.0, "Bregenz": 465.0},
   "Lienz":      {"Graz": 270.0, "Vienna": 400.0, "Eisenstadt": 437.0, "Bruck": 287.0, "Linz": 443.0, "Salzburg": 321.0, "Klagenfurt": 132.0, "Lienz": 0.0,   "Innsbruck": 157.0, "Munich": 298.0, "Bregenz": 332.0},
   "Innsbruck":  {"Graz": 435.0, "Vienna": 525.0, "Eisenstadt": 569.0, "Bruck": 479.0, "Linz": 378.0, "Salzburg": 265.0, "Klagenfurt": 301.0, "Lienz": 157.0, "Innsbruck": 0.0,   "Munich": 143.0, "Bregenz": 187.0},
   "Munich":     {"Graz": 375.0, "Vienna": 407.0, "Eisenstadt": 446.0, "Bruck": 339.0, "Linz": 265.0, "Salzburg": 132.0, "Klagenfurt": 443.0, "Lienz": 298.0, "Innsbruck": 143.0, "Munich": 0.0,   "Bregenz": 165.0},
   "Bregenz":    {"Graz": 450.0, "Vienna": 593.0, "Eisenstadt": 630.0, "Bruck": 521.0, "Linz": 456.0, "Salzburg": 301.0, "Klagenfurt": 465.0, "Lienz": 332.0, "Innsbruck": 187.0, "Munich": 165.0, "Bregenz": 0.0}}

    