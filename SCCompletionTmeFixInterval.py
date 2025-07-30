import random
import sys
import math
from collections import deque

class Packet:
    def __init__(self, sendTime, type, typeID):
        self.type = type
        self.typeID = typeID
        self.sendTime = sendTime

    def __eq__(self, other):
        return (
            self.type == other.type
            and self.typeID == other.typeID
            and self.sendTime == other.sendTime
        )



def analysis(loss_rate, repair_rate, total_packets=20, delay=500):

    Analysis_arrival_time = total_packets/(1-repair_rate)
    # Analysis_total_time = Analysis_arrival_time + repair_rate*(1-loss_rate)/(repair_rate-loss_rate)

    rho =(loss_rate*(1-repair_rate)) / (repair_rate*(1-loss_rate))
    Analysis_total_time = Analysis_arrival_time +rho+ rho*rho/2/(1-rho)

    print(f"\t(Analysis) Mean TotalTime runs: {Analysis_total_time :.2f}")
    print(f"\t(Analysis) Mean LastSourceArrivalTime runs: {Analysis_arrival_time:.2f}")
    return Analysis_total_time , Analysis_arrival_time


def run(loss_rate, repair_rate, random_seed, total_packets=200, delay=500):
    random.seed(random_seed)
    SystemTime = 0
    LastReceivedSourceID = -1
    LastSendSourceID = -1
    LastSendRepairID = -1
    LossList = []
    RepairCount = 0
    LastSourceArrivalTime = None
    channel = deque()

    SendRepairCount = 100
    SendSourceCount = int(100*(1-repair_rate)/repair_rate) #给予一个大的初始值以跳过初始阶段

    while True:
        if LastReceivedSourceID >= total_packets and not LossList:
            break

        # Send stage
        if LastSendSourceID < total_packets and (SendRepairCount/(SendRepairCount+SendSourceCount)) >= repair_rate:
            LastSendSourceID += 1
            SendSourceCount +=1
            pkt = Packet(SystemTime, "Source", LastSendSourceID)
        else:
            LastSendRepairID += 1
            SendRepairCount +=1
            pkt = Packet(SystemTime, "Repair", LastSendRepairID)
        channel.append(pkt)

        # Receive stage
        if channel and channel[0].sendTime + delay == SystemTime:
            recv = channel.popleft()
            if random.random() < loss_rate and recv.type == "Source":
                LossList.append(recv)
            else:
                if recv.type == "Repair" and LossList:
                    RepairCount += 1
                    if RepairCount == len(LossList):
                        for lost in LossList:
                            LastReceivedSourceID = max(LastReceivedSourceID, lost.typeID)
                            if lost.typeID == total_packets and LastSourceArrivalTime is None:
                                LastSourceArrivalTime = SystemTime
                        LossList.clear()
                        RepairCount = 0

                if recv.type == "Source":
                    LastReceivedSourceID = max(LastReceivedSourceID, recv.typeID)
                    if recv.typeID == total_packets and LastSourceArrivalTime is None:
                        LastSourceArrivalTime = SystemTime

        SystemTime += 1

    return SystemTime, LastSourceArrivalTime


def runsmple(loss_rate = 0.1,repair_rate = 0.16,total_packets = 200000 ,delay = 2000 ):
    # Parameters
    trials = 20000

    # Run simulations
    total_times = []
    arrival_times = []

    for i in range(trials):
        tot, arrival = run(loss_rate, repair_rate, random_seed=i, total_packets=total_packets, delay=delay)
        total_times.append(tot)
        arrival_times.append(arrival)

    # Calculate means
    mean_total_time = sum(total_times) / trials - delay
    mean_arrival_time = sum(arrival_times) / trials - delay
    print(f"Loss Rate {loss_rate} repair_rate {repair_rate} total_packets {total_packets} delay {delay}")
    print(f"\tMean TotalTime over {trials} runs: {mean_total_time:.2f}")
    print(f"\tMean LastSourceArrivalTime over {trials} runs: {mean_arrival_time:.2f}")

    Analysis_total_time , Analysis_arrival_time = analysis(loss_rate,repair_rate ,total_packets ,delay )

    Erroe_total_time= abs( (Analysis_total_time / mean_total_time) -1)
    Erroe_arrival_time= abs( (Analysis_arrival_time / mean_arrival_time) -1)
    print(f"\tError TotalTime: {Erroe_total_time:.5f}")
    print(f"\tError LastSourceArrivalTime: {Erroe_arrival_time:.5f}")

    sys.stdout.flush()
    sys.stderr.flush()  
    
if __name__ == "__main__" :
    runsmple(loss_rate = 0.01,repair_rate = 0.06)
    runsmple(loss_rate = 0.02,repair_rate = 0.07)
    runsmple(loss_rate = 0.03,repair_rate = 0.08)
    runsmple(loss_rate = 0.04,repair_rate = 0.09)
    runsmple(loss_rate = 0.05,repair_rate = 0.10)
    runsmple(loss_rate = 0.06,repair_rate = 0.11)
    runsmple(loss_rate = 0.07,repair_rate = 0.12)
    runsmple(loss_rate = 0.08,repair_rate = 0.13)
    runsmple(loss_rate = 0.09,repair_rate = 0.14)
    runsmple(loss_rate = 0.1,repair_rate = 0.15)
    runsmple(loss_rate = 0.11,repair_rate = 0.16)
    runsmple(loss_rate = 0.12,repair_rate = 0.17)
    runsmple(loss_rate = 0.13,repair_rate = 0.18)
    runsmple(loss_rate = 0.14,repair_rate = 0.19)
    runsmple(loss_rate = 0.15,repair_rate = 0.20)
    runsmple(loss_rate = 0.16,repair_rate = 0.21)
    runsmple(loss_rate = 0.17,repair_rate = 0.22)
    runsmple(loss_rate = 0.18,repair_rate = 0.23)
    runsmple(loss_rate = 0.19,repair_rate = 0.24)
    runsmple(loss_rate = 0.2,repair_rate = 0.25)