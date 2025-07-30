import random
import heapq
from collections import deque
import sys
import math

class Packet:
    def __init__(self, pkt_type, pkt_id, first_send_time, send_time):
        self.pkt_type = pkt_type      # "Source" or "Retrans"
        self.pkt_id = pkt_id
        self.first_send_time = first_send_time
        self.send_time = send_time
        self.retrans_times = 0

    def __lt__(self, other):
        return self.send_time < other.send_time

    def __repr__(self):
        return f"Packet(id={self.pkt_id}, type={self.pkt_type}, send_time={self.send_time}, retrans={self.retrans_times})"

def compute_EK(N, M, p, m_max=20):
    """
    Compute the expected last-arrival packet index E[K] for N packets,
    delay M, loss probability p, truncating retransmissions at m_max.
    """
    q = 1 - p
    E = 0.0
    # iterate over possible last packet index k
    for k in range(1, N + 1):
        Pk = 0.0
        # sum over m = number of attempts for packet k
        for m in range(1, m_max + 1):
            pmf = q * (p ** (m - 1))  # P(A_k = m)
            prod = 1.0
            # for every other packet i, probability it arrives before T_k = k + m*M
            for i in range(1, N + 1):
                if i == k:
                    continue
                # max retransmissions of packet i that arrive before T_k
                L = (k + M*m - i) // M
                prod *= (1 - p ** L)
            Pk += pmf * prod
        E += k * Pk
    return E

def compute_EM(e, P, tol=1e-12, max_k=10000):
    """
    Compute theoretical expectation E[M] = sum_{k=0}^∞ [1 - (1 - e^(k+1))^P]
    Truncate when the increment is below tol or k reaches max_k.
    """
    E_M = 0.0
    for k in range(max_k):
        term = 1 - (1 - e**(k+1))**P
        E_M += term
        if term < tol:
            break
    return E_M

def analysis(loss_rate, total_packets, delay):
    if total_packets > 2*delay:
        T_eff = total_packets/(1-loss_rate)-2*delay*loss_rate
        M=compute_EM(loss_rate,2*delay)
        K=compute_EK(2*delay, delay*2,loss_rate)
        T_tail = (M-1)*2*delay + K
    else:
        T_eff = total_packets/(1-loss_rate)-total_packets*loss_rate
        M=compute_EM(loss_rate,total_packets)
        K=compute_EK(total_packets, delay*2,loss_rate)
        T_tail = (M)*2*delay -(total_packets-K)

    Analysis_total_time = T_eff + T_tail
    print(f"\t(Analysis) Mean TotalTime runs: {Analysis_total_time :.2f}")
    print(f"\t(Analysis) Mean LastSourceArrivalTime runs: {T_eff:.2f}")
    print(f"\t(Analysis) Mean K: {K:.2f}")
    print(f"\t(Analysis) Mean M: {M:.2f}")

    return Analysis_total_time , T_eff , K


def run(loss_rate, random_seed, total_packets=2700, delay=500):
    random.seed(random_seed)
    
    sys_time = 0
    last_source_sent = 0
    loss_map = {}  # pkt_id -> loss count
    retrans_pq = []  # min-heap for retransmissions
    channel = deque()
    last_recv_id = -1
    last_retrans_count = 0
    receive_count = 0
    # 日志统计
    log = {
        "loss_count":     0,
        "receive_count":     0,
        "first_end_time": None,
        "first_end_loss": None,
        "loss_over_time": []
    }

    while True:
        # 终止条件
        if (last_source_sent == total_packets
            and not loss_map
            and not channel
            and not retrans_pq):
            break
        
        # 检查重传包是否到达发送时间
        if retrans_pq and retrans_pq[0].send_time == sys_time:
            pkt = heapq.heappop(retrans_pq)
            # print(f"Time {sys_time}: Retransmission packet ready to send -> {pkt}")
        else:
            pkt = None

        # 发送新包或重传包
        if pkt is None and last_source_sent < total_packets:
            last_source_sent += 1
            pkt = Packet("Source", last_source_sent, sys_time, sys_time)
            # print(f"Time {sys_time}: Sent new Source packet -> {pkt}")
        elif pkt:
            # print(f"Time {sys_time}: Sending retransmitted packet -> {pkt}")
            caca=1

        # 放入信道
        if pkt:
            channel.append(pkt)

        # 处理到达信道头部的包
        if channel and channel[0].send_time + delay == sys_time:
            pkt = channel.popleft()
            lost = (random.random() < loss_rate)

            if lost:
                # 丢包
                log["loss_count"] += 1

                loss_map[pkt.pkt_id] = loss_map.get(pkt.pkt_id, 0) + 1
                # print(f"Time {sys_time}: Packet lost -> {pkt}")

                if pkt.pkt_type == "Source" and pkt.pkt_id == total_packets:
                    log["first_end_time"] = sys_time - delay +1
                    log["first_end_loss"] = sum(loss_map.values())
                    log["receive_count"] = receive_count

                # 安排重传
                pkt.pkt_type = "Retrans"
                pkt.send_time = sys_time + delay
                pkt.retrans_times += 1
                heapq.heappush(retrans_pq, pkt)
                # print(f"Time {sys_time}: Scheduled retransmission -> {pkt}")
            else:
                # 成功接收
                # print(f"Time {sys_time}: Successfully received -> {pkt}")
                loss_map.pop(pkt.pkt_id, None)
                last_recv_id = pkt.pkt_id
                last_retrans_count = pkt.retrans_times

                receive_count+=1

                # 特殊记录最后一个包的首次到达
                if pkt.pkt_type == "Source" and pkt.pkt_id == total_packets:
                    log["first_end_time"] = sys_time - delay +1
                    log["first_end_loss"] = sum(loss_map.values())
                    log["receive_count"] = receive_count

        # 收集丢包统计
        log["loss_over_time"].append(sum(loss_map.values()))
        sys_time += 1

    # 计算平均丢包
    avg_loss = sum(log["loss_over_time"]) / len(log["loss_over_time"])
    # print(f"Total duration: {sys_time - delay}")
    # print(f"First arrival of packet {total_packets} at time: {log['first_end_time']}")
    # print(f"Loss count at first arrival: {log['first_end_loss']}")
    # print(f"Average loss over time: {avg_loss:.2f}")
    return {
        "loss_count":  log["loss_count"],
        "receive_count":  log["receive_count"],
        "total_duration": sys_time - delay,
        "first_end_time": log["first_end_time"],
        "first_end_loss": log["first_end_loss"],
        "LastReceiveID": last_recv_id,
        "last_retrans_count": last_retrans_count,
    }

def runsmple(loss_rate = 0.1,total_packets = 200000,delay = 2000 ):
    # Parameters
    trials = 20000

    # Run simulations
    total_times = []
    arrival_times = []
    first_end_loss = []
    Last_Receive_ID = []
    last_retrans_count =[]

    for i in range(trials):
        result = run(loss_rate, random_seed=i, total_packets=total_packets, delay=delay)
        total_times.append(result["total_duration"])
        arrival_times.append(result["first_end_time"])
        first_end_loss.append(result["first_end_loss"])
        Last_Receive_ID.append(result["LastReceiveID"])
        last_retrans_count.append(result["last_retrans_count"])

    # Calculate means
    mean_total_time = sum(total_times) / trials
    mean_arrival_time = sum(arrival_times) / trials
    mean_first_end_loss = sum(first_end_loss) / trials
    mean_Last_Receive_ID = sum(Last_Receive_ID) / trials
    mean_last_retrans_count = sum(last_retrans_count) / trials
    print(f"Loss Rate {loss_rate} total_packets {total_packets} delay {delay}")
    print(f"\tMean TotalTime over {trials} runs: {mean_total_time:.2f}")
    print(f"\tMean LastSourceArrivalTime over {trials} runs: {mean_arrival_time:.2f}")
    print(f"\tMean First End Loss Over {trials} runs: {mean_first_end_loss:.2f}")
    print(f"\tMean Last Receive ID {trials} runs: {mean_Last_Receive_ID:.2f}")
    print(f"\tMean Last Retrans Count {trials} runs: {mean_last_retrans_count:.2f}")

    Analysis_total_time , Analysis_arrival_time, Analysis_first_end_loss = analysis(loss_rate ,total_packets ,delay )

    Erroe_total_time= abs( (Analysis_total_time / mean_total_time) -1)
    Erroe_arrival_time= abs( (Analysis_arrival_time / mean_arrival_time) -1)
    Erroe_first_end_loss= abs( (Analysis_first_end_loss / mean_first_end_loss) -1)

    print(f"\tError TotalTime: {Erroe_total_time:.5f}")
    print(f"\tError LastSourceArrivalTime: {Erroe_arrival_time:.5f}")
    # print(f"\tError First End Loss: {Erroe_first_end_loss:.2f}")

    sys.stdout.flush()
    sys.stderr.flush()  
if __name__ == "__main__":
    # runsmple(loss_rate = 0.01)
    # runsmple(loss_rate = 0.02)
    # runsmple(loss_rate = 0.03)
    # runsmple(loss_rate = 0.04)
    # runsmple(loss_rate = 0.05)
    # runsmple(loss_rate = 0.06)
    # runsmple(loss_rate = 0.07)
    # runsmple(loss_rate = 0.08)
    # runsmple(loss_rate = 0.09)
    # runsmple(loss_rate = 0.1)
    # runsmple(loss_rate = 0.11)
    # runsmple(loss_rate = 0.12)
    # runsmple(loss_rate = 0.13)
    # runsmple(loss_rate = 0.14)
    # runsmple(loss_rate = 0.15)
    # runsmple(loss_rate = 0.16)
    # runsmple(loss_rate = 0.17)
    runsmple(loss_rate = 0.18)
    # runsmple(loss_rate = 0.19)
    # runsmple(loss_rate = 0.2)