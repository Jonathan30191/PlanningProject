import time
import pddl
import graph
import expressions
import pathfinding
import sys 

def plan(domain, problem, useheuristic=True):
    """
    Find a solution to a planning problem in the given domain 
    
    The parameters domain and problem are exactly what is returned from pddl.parse_domain and pddl.parse_problem. If useheuristic is true,
    a planning heuristic (developed in task 4) should be used, otherwise use pathfinding.default_heuristic. This allows you to compare 
    the effect of your heuristic vs. the default one easily.
    
    The return value of this function should be a 4-tuple, with the exact same elements as returned by pathfinding.astar:
       - A plan, which is a sequence of graph.Edge objects that have to be traversed to reach a goal state from the start. Each Edge object represents an action, 
         and the edge's name should be the name of the action, consisting of the name of the operator the action was derived from, followed by the parenthesized 
         and comma-separated parameter values e.g. "move(agent-1,sq-1-1,sq-2-1)"
       - distance is the number of actions in the plan (i.e. each action has cost 1)
       - visited is the total number of nodes that were added to the frontier during the execution of the algorithm 
       - expanded is the total number of nodes that were expanded (i.e. whose neighbors were added to the frontier)
    """

    goal = expressions.make_expression(problem[2][0])

    def heuristic(state, action):
        num = 1
        num = expressions.goalsAchieved(action.target.world, goal.getRoot(), num)
        num = 1/num
        #print(num)
        neighNum = len(state.neighbors)
        #print(neighNum)
        return num
        
    def isgoal(state):
        return True

    #Problem = [typesDictionary, initialStates, rawGoals, ExpressionGoal]
    #Domain = [actionsDictionary, typesDictionary]
    #print(problem[1])
    
    #expressions.printNAryTree(goal.getRoot())
    allPossibleActions = []

    #expressions.printNAryTree(goal.getRoot())
    
    start = graph.PlanNode(problem[1], domain[1], problem[0], [], 'Root')
    allPossibleActions = start.set_possibleActions(domain[0])
    start.set_initialStates()
    start.get_neighbors(allPossibleActions, domain[0], useheuristic)
    #for n in start.neighbors:
    #    print(n.name)
    #print(allPossibleActions)
    #astar(start, heuristic, goal, allActions, actionsDictionary)
    #input("Press Enter to continue...")
    #print(useheuristic)
    edgesPassed, totalPathCost, numFront, numExpandedNodes = pathfinding.astar(start, heuristic if useheuristic else pathfinding.default_heuristic, goal, allPossibleActions, domain[0], useheuristic)
    #returns priorityNode.edgesPassed, priorityNode.currentPathCost, numFrontier, expandedNodes

    return edgesPassed, len(edgesPassed), numFront, numExpandedNodes 

def main(domain, problem, useheuristic):

    t0 = time.time()
    
    (path,cost,visited_cnt,expanded_cnt) = plan(pddl.parse_domain(domain), pddl.parse_problem(problem), useheuristic)
    if useheuristic:
        print('')
        print('using heuristic')
        print('')
    else: 
        print('')
        print('without heuristic')
        print('')
    print("visited nodes:", visited_cnt, "expanded nodes:",expanded_cnt)
    if path is not None:
        print("Plan found with cost", cost)
        for n in path:
            print(n.name)
    else:
        print("No plan found")
    print("needed %.2f seconds"%(time.time() - t0))
    

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "-d" not in sys.argv)