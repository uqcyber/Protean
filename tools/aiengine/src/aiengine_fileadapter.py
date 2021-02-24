#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import sys
sys.path.append("/aiengine-1.9.0/src")
import pyaiengine
import json
import os
import time

class fileAdaptor(pyaiengine.DatabaseAdaptor):
    """ 
    Database adaptor for AIEngine, facilitates exporting
    packet scans to a JSON file.
    """

    def __init__(self, name):
        """ Opens file to write results to. """
        self.__f = open(name,"w")

    def __del__(self):
        """ Closes file. """
        self.__f.close()

    def update(self, key, data):
        """ Writes to file. """
        self.__f.write("%s\n" % (data))

    def insert(self, key):
      return

    def remove(self, key):
      return

def parse_protocol_summary(aiengine_stack, stdout_fd):
    """
    Calls an AIEngine method which outputs protocol statistics to stdout. 
    Reads a file which contains redirected stdout messages, skipping lines
    we do not want to store.

    An example line is:
        "IP 0 Bytes no 968 Bytes 2502083 968 Bytes 443683768 0 92 0"

    The Inner Loop is used to conjoin units (e.g. Bytes) to their preceding value.
    For example, in the above  [...,"968", "Bytes", ...] would become [..., "968 Bytes", ...]

    Results are stored in a dictionary and returned.
    """
    # print message to redirected stdout
    st.show_protocol_statistics()

    result = []
    units = ["Bytes", "KBytes", "MBytes"]
    with open("/stdout_temp.txt", "r") as f:
        for line in f:
            vals = line.split()
            if len(vals) == 0 or vals[0] in ["Protocol", "Total"]:
                continue
            
            # Inner Loop
            i = 0
            while i < (len(vals) - 1):
                if vals[i] in units:
                    vals[i - 1] = vals[i - 1] + " " + vals[i]
                    vals.remove(vals[i])
                i += 1
                    
            protocol_summary = {
            "protocol_name": vals[0],
            "bytes": vals[1],
            "packets": vals[2],
            "%_bytes": vals[3],
            "cache_miss": vals[4],
            "memory": vals[5],
            "use_memory": vals[6],
            "cache_memory": vals[7],
            "dynamic": vals[8],
            "events": vals[9],
            }
            result.append(protocol_summary)
    
    # clear stdout-redirect file
    os.ftruncate(fd, 0)

    return result

def parse_anomaly_summary(aiengine_stack, stdout_fd):
    """
    Calls an AIEngine method which outputs network anomaly statistics to stdout. 
    Reads a file which contains redirected stdout messages, skipping lines
    we do not want to store.

    An example line is:
        "Total TCP bad flags: 0"

    Results are stored in a dictionary and returned.
    """
    # print message to redirected stdout
    st.show_anomalies()

    anomaly_summary = {}
    with open("/stdout_temp.txt", "r") as f:
        for line in f:
            line = line.replace('\x00', '').strip()
            if len(line) == 0 or line == "Packet Anomalies":
                continue
            vals = line.split(":")
            # example vals: ['Total TCP bad flags:" '0']
            anomaly_summary[vals[0]] = int(vals[1]) 

    # clear stdout-redirect file
    os.ftruncate(fd, 0)
    return anomaly_summary

def parse_flows_summary(aiengine_stack, stdout_fd):
    """
    Calls an AIEngine method which outputs flow statistics to stdout. 
    Reads a file which contains redirected stdout messages, skipping lines
    we do not want to store.

    An example line is:
        "TCP:Flg[S(0)SA(0)A(4)F(0)R(0)P(1)Seq(16690613,3745726105)] 180 
        [192.168.2.15:443]:6:[192.168.100.5:58961] 4 TCPGenericProtocol"

    The Inner Loop facilitates values belonging to the 'info' key being combined into one
    (as 'info' values can contain white space, line.split() will have caused them 
    to separate into different array elements).
    This is achived by starting at the end of the parsed array and iterating backwards until
    the expected size of the array is reached, conjoining anything that extends beyong this limit.
    note: 'info' might be empty

    Results are stored in a dictionary and returned.
    """
    # print message to redirected stdout
    st.show_flows()

    result = []
    with open("/stdout_temp.txt", "r") as f:
        for line in f:
            line = line.replace('\x00', '').strip()
            vals = line.split()
            if len(line) == 0 or vals[0] in ["Flows", "Flow", "Total"]:
                continue
            # Inner Loop
            if len(vals) > 5:
                for i in range(len(vals) - 1, 4, -1):
                    vals[i - 1] = vals[i - 1] + " " + vals[i]
                    if i > 4:
                        vals.pop(i)

            flow_summary = {
            "flow": vals[0],
            "bytes": vals[1],
            "packets": vals[2],
            "flow_forwarder": vals[3],
            }
            # append info if this flow has any
            if len(vals) > 4:
                flow_summary["info"] = vals[4]

            result.append(flow_summary)

    # clear stdout-redirect file
    os.ftruncate(fd, 0)
    return result

def redirect_stdout_to_file(filepath):
    '''
    Used to redirect stdout to a file in order to capture and parse several information dumps AIEngine supports.
    The file should be truncated at the end of each data parse so the file may be reused by the next method.
    '''
    fd = os.open(filepath, os.O_RDWR | os.O_CREAT)
    os.ftruncate(fd, 0)
    os.dup2(fd, 1)
    return fd


if __name__ == '__main__':
    """ 
    Database adaptor for AIEngine, facilitates exporting
    packet scans to a JSON file and parsing protocol, network and anomaly summaries
    into a JSON format.

    Will scan all files in the /pcap directory.
    """

    # Load an instance of a LAN network & set max flows
    st = pyaiengine.StackLan()
    st.tcp_flows = 327680
    st.udp_flows = 163840
 
    # export to volume depending on if Protean use case or direct container usage
    output_path = "/aiengine/src/results/"
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    
    if os.path.isdir('/aiengine_vol/'):
        # volume existence means protean use-case
        output_path = "/aiengine_vol/"
        filename = "aiengine_pkt_results.json"

    # scan every file in the /pcap/ dir
    json_output = {}
    for filename in os.listdir("pcap"):
        print("[AIEngine] Scanning: " + filename)
        packet_dump_filename = "aiengine_packet_scans_{}_{}.json".format(
            filename, time.strftime('%H-%M-%S', time.localtime()))

        # update tcp & udp traffic every 16 packets
        db = fileAdaptor(output_path + packet_dump_filename)
        st.set_udp_database_adaptor(db, 16)
        st.set_tcp_database_adaptor(db, 16)

        with pyaiengine.PacketDispatcher("/pcap/" + filename) as pd:
            pd.stack = st
            pd.run()

        old_stdout_fd = os.dup(1)
        fd = redirect_stdout_to_file("/stdout_temp.txt")

        # parse redirected summary messages
        json_output[filename] = {
            "protocol_statistics": parse_protocol_summary(st, fd),
            "flow_statistics": parse_flows_summary(st, fd),
            "anomaly_statistics": parse_anomaly_summary(st, fd)
        }

        # put stdout back
        os.dup2(old_stdout_fd, 1)
        os.close(fd)
        os.remove("/stdout_temp.txt")

    # print summary statistics to a different file
    with open(output_path + 'aiengine_results.json', 'w') as fp:
        json.dump(json_output, fp)

    sys.exit(0)