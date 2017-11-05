# operations-research-project
A code demonstration of my use of the Linear and Integer programming package gurobi as part of an assignment for university. A achieved a High Distinction in this course with full marks in this assignment.

The situation 
```python

from gurobipy import *
import random

random.seed(19)

# Sets
# Customers
C = range(10)
# Time periods
Months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
T = range(6)
# Blocks
Row = range(4)
Col = range(7)

# Data
Demand = [[random.randint(45000,55000) for t in T] for c in C]
minAl = [random.randint(520,580)/10.0 for c in C]
minSi = [random.randint(40,60)/10.0 for c in C]

Tonnage = [[random.randint(170000,250000) for j in Col] for i in Row]
Al = [[random.randint(530,580)/10.0 for j in Col] for i in Row]
Si = [[random.randint(45,60)/10.0 for j in Col] for i in Row]
Cost = [[random.randint(70,130)/10.0-i for j in Col] for i in Row]
```
