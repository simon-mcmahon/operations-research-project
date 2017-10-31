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


#-------------------------------
#CHOOSE THE BLOCK ALGORITHM VARIANT
#False = First Method (No mining unless block above in row mined)
#True = Second Method (No mining unless all above ajacent blocks mined)

Activate_Updated_Condition = True

#---------------------------------


#Define the Model

m = Model("BigAlCo_v2")

#Define Variables

X={}
Z={}

#Note the upper bound of X as the tonnage of a particular block

for i in Row:
    for j in Col:
        for t in T:
            for c in C:
                X[i,j,t,c] = m.addVar(vtype=GRB.CONTINUOUS,ub=Tonnage[i][j])
                

for i in Row:
    for j in Col:
        for t in T:
            Z[i,j,t]=m.addVar(vtype=GRB.BINARY)

#Update the model to include the variables

m.update()

#set the Objective

m.setObjective(quicksum(X[i,j,t,c]*Cost[i][j] for i in Row for j in Col for t in T for c in C),GRB.MINIMIZE)

#Add the Constraints

#Delivery or Ore to customers

for t in T:
    for c in C:
        m.addConstr(quicksum(X[i,j,t,c] for i in Row for j in Col) >= Demand[c][t])


#Aluminium and Silicon Cosntraints

for t in T:
    for c in C:
        m.addConstr(quicksum( X[i,j,t,c]*(Al[i][j]-minAl[c]) for i in Row for j in Col) >= 0)
        m.addConstr(quicksum( X[i,j,t,c]*(Si[i][j]-minSi[c]) for i in Row for j in Col) >= 0)

#Max Allowable from Each mine
for i in Row:
    for j in Col:
        m.addConstr( quicksum( X[i,j,t,c] for c in C for t in T) <= Tonnage[i][j])

#Logical Constraints

#If the cumulative amount mined from a particular block is less than the Tonnage, force Z[i,j,t]==0

for t in T:
    t_cumul=range(t+1)
    for i in Row:
        for j in Col:
            m.addConstr(quicksum(X[i,j,t_new,c] for c in C for t_new in t_cumul) >= Z[i,j,t]*Tonnage[i][j])

#Preserve the exhaustion of a mined site forward in time

for i in Row:
    for j in Col:
        for t in T[:-1]: #All but the last month
            m.addConstr(Z[i,j,t+1]>=Z[i,j,t])

#If the previous Row in the Same Column mined out (Z[i-1,j,t]=1) then permit amount mined to be non-zero
#This is handled with a relaxed less than or equal to expression
#Upper bound handled in variable definition

for t in T:
    for j in Col:
        for i in Row[1:]:
            m.addConstr( quicksum(X[i,j,t,c] for c in C) <= (Tonnage[i][j]+1000000)*Z[i-1,j,t] )

#Additonal Constraints for the updated Block Algorithm applied if variable True

if Activate_Updated_Condition == True:

    for t in T:
        for i in Row[1:]:
            for j in Col[1:]:
                m.addConstr( quicksum(X[i,j,t,c] for c in C) <= (Tonnage[i][j]+1000000)*Z[i-1,j-1,t] )
    
    #Same form as above condition but for top right block
    #Note that First row and last column as this condition does not exist there
    
    for t in T:
        for i in Row[1:]:
            for j in Col[:-1]:
                m.addConstr( quicksum(X[i,j,t,c] for c in C) <= (Tonnage[i][j]+1000000)*Z[i-1,j+1,t] ) 

#Rainy Season Constraints

for t in [4,5]:
    for j in [0,1]:
        for i in Row:
            for c in C:
                m.addConstr(X[i,j,t,c] <= 0)

#Solve the problem

m.optimize()

#Output data for the report section

#Show Objective Value
print "--------------"
print "Minimum Total Mining Cost"
print m.ObjVal
print "--------------"


#Noteable events for each time period

#Print total amount mined from each block

for t in T:
    print "Time " + str(t) + " Noteable Events"
    mined_blocks=[]
    for i in Row:
        for j in Col:
            for c in C:
                if X[i,j,t,c].x != 0:
                    mined_blocks += [ (i,j) ]
                    break
    for k in range(len(mined_blocks)):
        total_mined=0
        i_row = int(mined_blocks[k][0])
        j_col = int(mined_blocks[k][1])
        
        for c in C:

            total_mined += X[i_row,j_col,t,c].x
        
        if total_mined > 0.01 : #Eliminate the rounding errors of Gurobi
            print str(total_mined) + " Tonnes from Block " + " " + str(mined_blocks[k])
    print "----------------------"

#Generation of a progressive Mined matrix for the blocks. 
#Value 1 if mined from at end of time period t, 2 if exhausted
print " --------------"
print "Cumulative Mined Matrix"
print " -----------------"


for t in T:
    print "Time " + str(t)
    
    for i in Row:
        row_str=''
        
        for j in Col:
            prog_mined = 0            
            for c in C:
                for t_prog in range(t+1):
                    
                    prog_mined += X[i,j,t_prog,c].x
            
            if prog_mined >= 0.01 and int(Z[i,j,t].x) > 0.9:
                row_str += "2 "
            elif prog_mined >= 0.01:
                row_str += "1 "
            else:
                row_str += "0 "
        
        print row_str

#Mined in each time period

print "------------------"
print "Total amount mined from each block in each time period"
print "-----------------"

for t in T:
    print "Time " + str(t)
    for i in Row:
        row_str=''
        for j in Col:
            col_sum=0            
            for c in C:
                col_sum+=X[i,j,t,c].x
            row_str+=str(col_sum) + ' '
        print row_str

#Total Mined Matrix

print "------------------"
print "Total amount mined from each block across all time"
print "-----------------"
for i in Row:
    row_str=''
    for j in Col:
        col_sum=0            
        for c in C:
            for t in T:
                col_sum+=X[i,j,t,c].x
        row_str+=str(col_sum) + ' '
    print row_str

#Print the z-matrix

print " -----------"
print "Exhausted Mines in time"
print "------------"

for t in T:
    print "Time " + str(t)
    for i in Row:
        row_str=''
        for j in Col:            
            row_str += str(int(Z[i,j,t].x)) + " "
        print row_str