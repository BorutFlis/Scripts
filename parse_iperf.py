import re
import pandas as pd
import os

tcp_dict={
    "TCP_avg_trf_uplink":[1,0],
    "TCP_avg_trf_uplink (unit)":[1,1],
    "TCP_avg_bitrate_uplink":[1,2],
    "TCP_avg_bitrate_uplink (unit)":[1,3],
    'TCP_avg_trf_downlink':[0,0],
    'TCP_avg_trf_downlink (unit)':[0,1],
    'TCP_avg_bitrate_downlink':[0,2],
    'TCP_avg_bitrate_downlink (unit)':[0,3],
    'TCP_avg_bitrate_downlink Retr':[0,4]
}

udp_dict={
    'UDP_avg_trf_uplink':[1,0],
    'UDP_avg_trf_uplink (unit)':[1,1],
    'UDP_avg_bitrate_uplink':[1,2],
    'UDP_avg_bitrate_uplink (unit)':[1,3],
    'UDP_avg_jitter_uplink':[1,4],
    'UDP_avg_lost_dat_uplink':[1,6],
    'UDP_avg_total_dat_uplink':[1,7],
    'UDP_avg_dat_percent_uplink':[[1,6],[1,7],lambda x,y: int(x)/int(y) if int(y)>0 else 0],
    'UDP_avg_trf_downlink':[0,0],
    'UDP_avg_trf_downlink (unit)':[0,1],
    'UDP_avg_bitrate_downlink':[0,2],
    'UDP_avg_bitrate_downlink (unit)':[0,3],
    'UDP_avg_jitter_downlink':[0,4],
    'UDP_avg_lost_dat_downlink':[0,6],
    'UDP_avg_total_dat_downlink':[0,7],
    'UDP_avg_dat_percent_downlink':[[0,6],[0,7],lambda x,y: int(x)/int(y) if int(y)>0 else 0]
}

prot_dict=[tcp_dict,udp_dict]

avg_regex=[
    [#regex for TCP
        "(?<=sec)\s+(\d+\.?\d*)\s+(\w+)\s+(\d+\.?\d*)\s+(\w+/\w+)\s+(\d+)?\s+(?:sender)",
        "(?<=sec)\s+(\d+\.?\d*)\s+(\w+)\s+(\d+\.?\d*)\s+(\w+/\w+)\s+(?:receiver)"
    ],
    [#regex for UDP
        "(?<=sec)\s+(\d+\.?\d*)\s+(\w+)\s+(\d+\.?\d*)\s+(\w+/\w+)\s+(\d+\.\d+) (\w+)\s+(\d+)/(\d+)\s+(?:\(.+%\))\s+(?:sender)",
        "(?<=sec)\s+(\d+\.?\d*)\s+(\w+)\s+(\d+\.?\d*)\s+(\w+/\w+)\s+(\d+\.\d+) (\w+)\s+(\d+)/(\d+)\s+(?:\(.+%\))\s+(?:receiver)"
    ]
]




def parse_logs(folder="logs"):
    df_example = pd.read_csv(os.path.join(folder,"iperf_logs.csv"), header=1)
    for f in os.listdir(folder):
        f_open = open(os.path.join(folder,f), "rt")
        df = pd.DataFrame(columns=df_example.columns)
        log_text = f_open.read()
        time_stamps = log_text.split("==============================")[1:]
        for i in range(len(time_stamps)):
            ips=[]
            m = re.search("(?<=\+{30}\nTCP\n\+{30}\n)([\s\S]*?)(?=\+{30})", time_stamps[i])
            m1= re.search("(?<=\+{30}\nUDP\n\+{30}\n)([\s\S]*?)(?=\+{30})", time_stamps[i])
            ts=re.match("\n?(\d{2}:\d{2}:\d{2})",time_stamps[i])
            rtt=re.search("(?<=rtt min/avg/max/mdev = )(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)",time_stamps[i])
            append_dict = {"Time": ts.groups()[0]}
            if rtt is not None:
                append_dict.update({"RTT min":rtt.groups()[0], "RTT avg":rtt.groups()[1], "RTT max":rtt.groups()[2], "RTT mdev":rtt.groups()[3]})
            for idx, prot in enumerate([m,m1]):
                if prot is not None:
                    ip_addr=re.search("(?<=Connecting to host )(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",prot.groups()[0])
                    if ip_addr is not None:
                        ips.append(ip_addr.groups()[0])
                    avg_section = re.search("(?<=(?:\- ){24}\-\n)([\s\S]+)", prot.groups()[0])
                    if avg_section is not None:
                        lines = re.findall("(?<=\[  5\])([ \S]+)\n",avg_section.groups()[0])
                        if len(lines) == 2:
                            down=re.search(avg_regex[idx][0],lines[0])
                            up=re.search(avg_regex[idx][1],lines[1])
                            if up is None or down is None:
                                print(f)
                                print(ts.groups()[0])
                                print(lines[0])
                                print(lines[1])
                            vals=[down.groups(),up.groups()]
                            for k,v in prot_dict[idx].items():
                                if len(v)>2:
                                    l_idx=v[0][0]
                                    l=vals[l_idx]
                                    append_dict[k]=v[2](l[v[0][1]], l[v[1][1]])
                                else:
                                    append_dict[k]=vals[v[0]][v[1]]
            for i,ip in enumerate(ips[:4]):
                append_dict["IP "+str(i+1)]=ip
            df=df.append(append_dict,ignore_index=True)
        df.to_csv(f+".csv")

parse_logs("logs")