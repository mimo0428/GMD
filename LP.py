from gurobipy import *
from Schetch import *
from main import timeMax

x = {}
X = {}
XX = {}
C = {}  # 定义字典用来存放决策变量

# 得到调度方案
def getLPScheduling(data):
    # Create a new model
    m = Model("scheduling")
    # 定义决策变量，并加入模型中


    for k in data.existApplication:
        name = 'C_' + str(k)
        C[k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=name)  # 定义访问时间为连续变量

        X[k] = {}
        XX[k] = {}

        for t in range(timeMax):
            name = 'X_' + str(k) + '(' + str(t) + ')'
            X[k][t] = m.addVar(0, 1, vtype=GRB.CONTINUOUS, name=name)  # 定义访问时间为连续变量
            name = "XX_" + str(k) + "(" + str(t) + ")"
            XX[k][t] = m.addVar(0, 1, vtype=GRB.CONTINUOUS, name='name')

    for key in data.flows:
        i = key[0]
        k = key[1]


        x[i,k] = {}
        for t in range(timeMax):
            name = 'x_' + str(i) + '_' + str(k) + '(' + str(t) + ')'
            x[i,k][t] = m.addVar(0, 1, vtype=GRB.CONTINUOUS, name=name)

    #  目标函数
    # 首先定义一个线性表达式
    obj = LinExpr(0)
    for k in data.existApplication:
        w = data.application[k].weight
        # 将目标函数系数与决策变量相乘，并进行连加
        obj.addTerms(w, C[k])
    # 将表示目标函数的线性表达式加入模型，并定义为求解最小化问题
    m.setObjective(obj, GRB.MINIMIZE)

    # constraint 1
    for key in data.flows:
        i = key[0]
        k = key[1]
        expr = LinExpr(0)
        for t in range(timeMax):
            # 约束系数与决策变量相乘
            expr.addTerms(1, x[i, k][t])
        # 将约束加入模型
        m.addConstr(expr == 1, name='flow_full_scheduled_' + str(i) + '_' + str(k))

    # constraint 2
    for k in data.existApplication:
        for t in range(timeMax):
            # 左边式子
            expr1 = LinExpr(0)
            expr1.addTerms(1, X[k][t])
            for key in data.flows:
                i = key[0]
                tk = key[1]
                if tk == k:
                    expr2 = LinExpr(0)
                    for tt in range(t+1):

                        expr2.addTerms(1, x[i, tk][tt])
                    # print('--')
                    # print(k, t, i, tk, tt)
                    m.addConstr(expr1 <= expr2, name='coflow_full_scheduled_' + str(i) + '_' + str(k))

    # constraint 3
    for k in data.existApplication:
        expr66 = LinExpr(0)
        expr66.addTerms(1, C[k])
        expr6 = LinExpr(0)
        for t in range(timeMax):
            m.addConstr(XX[k][t] == 1 - X[k][t], name="C_constraint" + "_" + str(k))
            expr6.addTerms(1, XX[k][t])
        m.addConstr(1 + expr6 <= expr66, name='C_constraint' + '_' + str(k))

    # constraint 6
    for t in range(timeMax):
        expr = [[LinExpr(0) for i in range(len(data.bandwidth))] for j in range(len(data.bandwidth))]
        for key in data.flows:
            i = key[0]
            k = key[1]
            for p in data.flows[key].path:
                ii = p[0]
                jj = p[1]
                if ii > jj:
                    ii, jj = jj, ii
                expr[ii][jj].addTerms(data.flows[key].demand, x[i, k][t])

        for ii in range(len(data.bandwidth)):
            for jj in range(len(data.bandwidth)):
                m.addConstr(expr[ii][jj] <= data.bandwidth[ii][jj],
                            name='C_constraint path' + str(ii) + '_' + str(jj) + 'at time ' + str(t))


    # 求解
    m.optimize()
    print("\n\n-----optimal value-----")
    print(m.ObjVal)

    for key in x.keys():
        # print(key[0])
        for t in range(timeMax):
            if x[key][t].x > 0:
                print(x[key][t].VarName + ' = ' + str(x[key][t].x))

    for key in C.keys():
        if C[key].x > 0:
            print(C[key].VarName + ' = ', C[key].x)

    for key in X.keys():
        for t in range(timeMax):
            if X[key][t].x > 0:
                print(X[key][t].VarName + ' = ', X[key][t].x)



###########################################
# stretch the LP schedule
    lamda = getRamdomNumber()
    print("lambda:" + str(lamda))

    for key in data.flows:
        i = key[0]
        k = key[1]
        isFullScheduled = 0

        # 图3
        # 对所有流的所有时间段进行遍历
        for t in range(timeMax):
            print("t:" + str(t))
            if x[i, k][t].x > 0:
                print("x[i, k][t].x:" + ",i:"+ str(i) + ",k:" + str(k) + "," +  str(x[i, k][t].x))
                if isFullScheduled < 1:

                    isFullScheduled = x[i, k][t].x/lamda + isFullScheduled
                    print("isFullScheduled:" + str(isFullScheduled))
                    t1 = t / lamda
                    t2 = (t + 1) / lamda

                    if isFullScheduled >= 1:
                        print("nt2:" + str(t2))
                        remain = isFullScheduled - 1
                        print("remain:"+str(remain))
                        t2 = t2 - remain / x[i, k][t].x
                        print("nowt2:" + str(t2))
                        data.flows[key].cct1 = t2
                        data.flows[key].cct2 = t2
                        isFullScheduled = 1

                    data.flows[key].schedule[t1, t2] = x[i, k][t].x

                    # 将调度信息存放到所有该流经过的路径
                    # 以时间为索引，存放流索引和在该时间调度的数据量
                    # print(data.allPath)
                    for p in data.flows[key].path:
                        print(p)
                        data.allPath[p].timeSet[t1, t2] = ((i, k), x[i, k][t].x)

                # x[i, k][t].x = 0

        # 图4 直到没有改变，停止遍历
        # 对每一条链路进行遍历：
        # 如果有哪段时间为空，考虑将后面的时间段前移，判断其其他链路上的该段时间对于该流是否为空，如果是，将其前移
        isChanged = 1
        while isChanged:
            isChanged = 0
            for pij in data.allPath:
                sortedTime = sorted(data.allPath[pij].timeSet.keys())  # 对时间进行排序
                for t in range(len(sortedTime)):
                    flow = data.allPath[pij].timeSet[sortedTime[t][0], sortedTime[t][1]][0]
                    # 判断时间上是否有空余位置
                    res = 0
                    if t == 0:
                        if not isFloatEqual(sortedTime[0][0], 0):
                            t1 = 0
                            t2 = sortedTime[0][0]
                            res = checkCanForward(t1, t2, flow[0], flow[1], data)
                    else:
                        if not isFloatEqual(sortedTime[t-1][1], sortedTime[t][0]) and sortedTime[t][0] > sortedTime[t-1][1]:
                            t1 = sortedTime[t-1][1]
                            t2 = sortedTime[t][0]
                            res = checkCanForward(t1, t2, flow[0], flow[1], data)
                    # 可以前移
                    if res == 1:
                        isChanged = 1
                        nt1 = t1
                        oslot = sortedTime[t][1] - sortedTime[t][0]
                        nslot = t2 - t1
                        if nslot >= oslot:
                            nt2 = t2 - (nslot - oslot)
                        else:
                            nt2 = t2 + (oslot - nslot)
                        MoveFoward(sortedTime[t][0], sortedTime[t][1], nt1, nt2, flow[0], flow[1], data)
                        break
