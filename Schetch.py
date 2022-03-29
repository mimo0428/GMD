from invertCDF import getRamdomNumber
from math import fabs
# from main import timeMax

def isFloatEqual(xx,yy):
    if fabs(xx - yy) <= 1e-6:
        return True
    return False

# 判断其其他链路上的该段时间对于该流是否为空，如果是，将其前移
def checkCanForward(t1, t2, i, k, data):
    canMoveForward = 1
    for p in data.flows[i, k].path:
        ii = p[0]
        jj = p[1]
        for time in data.allPath[p].timeSet:
            if time[0] < t1 < time[1] or time[0] < t2 < time[1]:
                canMoveForward = 0
                return canMoveForward
    return canMoveForward

def MoveFoward(ot1, ot2, nt1, nt2, i, k, data):
    data.flows[i, k].schedule[nt1, nt2] = data.flows[i, k].schedule[ot1, ot2]

    if data.flows[i, k].cct2 > nt2:
        data.flows[i, k].cct2 = nt2

    index = 1
    for p in data.flows[i, k].path:
        if index == 1:
            index = 0
            del data.allPath[p].timeSet[ot1, ot2, i, k]
        data.allPath[p].timeSet[nt1, nt2, i, k] = ((i, k), data.flows[i, k].schedule[ot1, ot2])

    data.flows[i, k].schedule.pop((ot1, ot2))

# def stretchLp(data):
#     # stretch the LP schedule
#     lamda = getRamdomNumber()
#     for key in data.flows:
#         i = key[0]
#         k = key[1]
#         isFullScheduled = 0
#
#         # 图3
#         # 对所有流的所有时间段进行遍历
#         for t in range(timeMax):
#             print(x[i, k][t].x)
#             if x[i, k][t].x > 0:
#                 if isFullScheduled < 1:
#                     isFullScheduled = x[i, k][t].x / lamda + isFullScheduled
#                     t1 = t / lamda
#                     t2 = (t + 1) / lamda
#
#                     if isFullScheduled >= 1:
#                         remain = isFullScheduled - 1
#                         t2 = t2 - remain * lamda
#                         data.flows[key].cct1 = t2
#                         data.flows[key].cct2 = t2
#                         isFullScheduled = 1
#
#                     data.flows[key].schedule[t1, t2] = x[i, k][t].x
#
#                     # 将调度信息存放到所有该流经过的路径
#                     # 以时间为索引，存放流索引和在该时间调度的数据量
#                     for p in data.flows[key].path:
#                         data.allPath[p].timeSet[t1, t2] = ((i, k), x[i, k][t].x)
#
#                 x[i, k][t].x = 0
#
#         # 图4 直到没有改变，停止遍历
#         # 对每一条链路进行遍历：
#         # 如果有哪段时间为空，考虑将后面的时间段前移，判断其其他链路上的该段时间对于该流是否为空，如果是，将其前移
#         isChanged = 1
#         while isChanged:
#             isChanged = 0
#             for pij in data.allPath:
#                 sortedTime = sorted(data.allPath[pij].timeSet.keys())  # 对时间进行排序
#                 for t in range(len(sortedTime)):
#                     flow = data.allPath[pij].timeSet[sortedTime[t][0], sortedTime[t][1]][0]
#                     # 判断时间上是否有空余位置
#                     if t == 0:
#                         if not isFloatEqual(sortedTime[0][0], 0):
#                             t1 = 0
#                             t2 = sortedTime[0][0]
#                             res = checkCanForward(t1, t2, flow[0], flow[1], data)
#                     else:
#                         if not isFloatEqual(sortedTime[t - 1][1], sortedTime[t][0]) and sortedTime[t][0] > \
#                                 sortedTime[t - 1][1]:
#                             t1 = sortedTime[t - 1][1]
#                             t2 = sortedTime[t][0]
#                             res = checkCanForward(t1, t2, flow[0], flow[1], data)
#                     # 可以前移
#                     if res == 1:
#                         isChanged = 1
#                         nt1 = t1
#                         oslot = sortedTime[t][1] - sortedTime[t][0]
#                         nslot = t2 - t1
#                         if nslot >= oslot:
#                             nt2 = t2 - (nslot - oslot)
#                         else:
#                             nt2 = t2 + (oslot - nslot)
#                         MoveFoward(sortedTime[t][0], sortedTime[t][1], nt1, nt2, flow[0], flow[1], data)
#                         break

def calTime(data):
    allC1 = 0
    allC2 = 0
    for key in data.flows:
        w = data.flows[key].weight
        c1 = data.flows[key].cct1
        c2 = data.flows[key].cct2
        print(key)
        print("c1: " + str(c1) + ",c2: " + str(c2) + ",weight:" + str(w))
        allC1 += c1 * w
        allC2 += c2 * w
    print('cct1:'+str(allC1))
    print('cct2:' + str(allC2))
