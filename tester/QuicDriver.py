#!/usr/bin/python

from __future__ import print_function
import sys
import argparse
import json
import math
from warnings import catch_warnings
from time import sleep
import QuicPktBuilder
import scapy, scapy.all

# get TRex APIs.
sys.path.insert(0, "/opt/trex-core-3.08/trex_client/interactive/")

from trex_stl_lib.api import *


class QuicOutput:
    def __init__(self):
        # We use a dictionary to represent (internally) the QuicOutput 'class'.
        self.output = {}

        # We create and return a dictionary used to store results of the run.
        # The dictionary is composed by:
        #
        # dictionary
        #     |
        #     +--tx
        #     |   +--port
        #     |   +--total_packets
        #     |
        #     +--rx
        #     |   +--port
        #     |   +--total_packets
        #     |
        #     +--warnings

        self.output["tx"] = {}
        self.output["rx"] = {}
        self.output["tx"]["port"] = -1
        self.output["tx"]["total_packets"] = -1
        self.output["tx"]["duration"] = -1
        self.output["tx"]["requested_tx_rate"] = -1

        self.output["rx"]["port"] = -1
        self.output["rx"]["total_packets"] = -1
        self.output["warnings"] = None

    def setTxPort(self, txPort):
        self.output["tx"]["port"] = txPort

    def setRxPort(self, rxPort):
        self.output["rx"]["port"] = rxPort

    def setTxTotalPackets(self, tPackets):
        self.output["tx"]["total_packets"] = tPackets

    def setRxTotalPackets(self, tPackets):
        self.output["rx"]["total_packets"] = tPackets

    def setTxDuration(self, duration):
        self.output["tx"]["duration"] = duration

    def setRequestedTxRate(self, rate):
        self.output["tx"]["requested_tx_rate"] = rate

    def setWarnings(self, warn):
        self.output["warnings"] = warn

    def getTxPort(self):
        return self.output["tx"]["port"]

    def getRxPort(self, rxPort):
        return self.output["rx"]["port"]

    def getTxTotalPackets(self):
        return self.output["tx"]["total_packets"]

    def getRxTotalPackets(self):
        return self.output["rx"]["total_packets"]

    def getTxDuration(self):
        return self.output["tx"]["duration"]

    def getRequestedTxRate(self):
        return self.output["tx"]["requested_tx_rate"]

    def getWarnings(self):
        return self.output["warnings"]

    def toDictionary(self):
        return self.output

    def toString(self):
        return str(self.output)


def wait_files(files: list, tick_time=0.1, timeout: int = 10):
    counter = 0
    while counter < timeout:
        try:
            if all(os.path.exists(f) and os.path.isfile(f) for f in files):
                break
        except IOError as e:
            pass
        sleep(tick_time)
        counter += tick_time


class QuicDriver:
    # Builds an instance of QuicDriver
    def __init__(self, server, txPort, rxPort, pcap, rate, duration):
        self.server = server
        self.txPort = txPort
        self.rxPort = rxPort
        self.pcap = pcap
        self.rate = rate
        self.duration = duration

    # It creates a stream by leveraging the 'pcap' file which has been set
    # during the driver creation.
    def __buildStreamsFromPcap(self):
        referencePkt = scapy.all.rdpcap(self.pcap)[0]
        sip = referencePkt[IP].src
        dip = referencePkt[IP].dst
        sport = referencePkt[UDP].sport
        dport = referencePkt[UDP].dport
        pkt: scapy.packet.Packet = QuicPktBuilder.buildInitialForceVersionNegotiation(sip, dip, sport, dport)
        vm: STLVM = STLVM()
        # vm.var(name="sip", min_value="192.168.10.2", max_value="192.168.10.254", size=4, op="inc")
        vm.var(name="sport", min_value=0x1000, max_value=0xFFFF, size=2, op="inc")
        vm.var(name="dcid", min_value=0x1000000000000000, max_value=0xFFFFFFFFFFFFFFFF, size=8, op="inc")
        vm.var(name="scid", min_value=0x2000000000000000, max_value=0xFFFFFFFFFFFFFFFF, size=8, op="inc")
        # vm.write(fv_name="sip", pkt_offset="IP.src")
        vm.write(fv_name="sport", pkt_offset="UDP.sport")
        vm.write(fv_name="dcid", pkt_offset=0x30)
        vm.write(fv_name="scid", pkt_offset=0x39)
        vm.add_cmd(STLVmFixChecksumHw(l3_offset="IP", l4_offset="UDP", l4_type=CTRexVmInsFixHwCs.L4_TYPE_UDP))

        pktBuilder = STLPktBuilder(pkt=pkt, vm=vm)

        # pktBuilder = STLPktBuilder(pkt=self.pcap)

        return [STLStream(packet=pktBuilder, mode=STLTXCont())]
        # return [STLStream(packet=pktBuilder, mode=STLTXSingleBurst())]

    def run(self):
        tOutput = QuicOutput()
        tOutput.setTxPort(self.txPort)
        tOutput.setRxPort(self.rxPort)
        tOutput.setRequestedTxRate(self.rate)
        tOutput.setTxDuration(self.duration)
        drop_file = "/tmp/srperf_quic_driver/dropped_packets.txt"
        dup_file = "/tmp/srperf_quic_driver/duplicated_packets.txt"
        ready_file = "/tmp/srperf_quic_driver/ready.txt"

        # We create the client
        client = STLClient(server=self.server)
        try:
            txStats = None
            rxStats = None
            allPorts = list(set([self.txPort, self.rxPort]))

            client.connect()

            # For safety reasons we reset any counter.
            client.reset(ports=allPorts)

            # We retrieve the streams
            # NOTE: we have as many streams as captured packets within
            # the .pcap file.
            streams = self.__buildStreamsFromPcap()

            # We use only one port to multiplex altogether streams.
            client.add_streams(streams, ports=[self.txPort])

            if os.environ.get("ENABLE_SYNC"):
                if os.environ.get("MANUAL_SYNC"):
                    print("Waiting for server side ready")
                    input()
                else:
                    print("Waiting for server side ready")
                    wait_files([ready_file])
            # Even if we create a new client it is better to reset also
            # ports and streams, because between client creation and
            # start of the experiment some packets may be received on ports.
            client.clear_stats()

            client.start(ports=[self.txPort], mult=self.rate, duration=self.duration)

            # Now we block until all packets have been sent/received. To
            # for be sure operations had been completed we wait for both
            # txPort and rxPort.
            client.wait_on_traffic(ports=allPorts)

            # We store warnings inside the dictionary in order to allow them
            # to be accessed afterwards
            warn = client.get_warnings()
            if warn:
                tOutput.setWarnings(warn)

            dropped_packets = 0
            duplicated_packets = 0
            if os.environ.get("ENABLE_SYNC"):
                os.makedirs("/tmp/srperf_quic_driver", exist_ok=True)
                if os.environ.get("MANUAL_SYNC"):
                    print("Waiting for server side packet data")
                    print("Dropped packets: ")
                    dropped_packets = int(input())
                    print("Duplicate packets: ")
                    duplicated_packets = int(input())
                else:
                    print("Waiting for server side packet data")
                    wait_files([drop_file, dup_file])
                    try:
                        with open(drop_file, "r") as f:
                            dropped_packets = int(f.read())
                            print(f"Dropped packets: {dropped_packets}")
                    except (ValueError, IOError) as e:
                        print(f"Exception while accessing {drop_file}: {e}")
                    try:
                        with open(f"/tmp/srperf_quic_driver/duplicated_packets.txt", "r") as f:
                            duplicated_packets = int(f.read())
                            print(f"Duplicated packets: {duplicated_packets}")
                    except (ValueError, IOError) as e:
                        print(f"Exception while accessing {dup_file}: {e}")

            # We wait for a bit in order to let the counters be stable
            sleep(1)
            # We retrieve statistics from Tx and Rx ports.
            txStats = client.get_xstats(self.txPort)
            rxStats = client.get_xstats(self.rxPort)
            # tOutput.setTxTotalPackets(txStats["tx_total_packets"])
            # tOutput.setRxTotalPackets(rxStats["rx_total_packets"])
            tOutput.setTxTotalPackets(txStats["tx_phy_packets"] - dropped_packets)
            tOutput.setRxTotalPackets(rxStats["rx_phy_packets"] - duplicated_packets)

        except STLError as e:
            print(e)
            sys.exit(1)

        finally:
            try:
                client.disconnect()
            except Exception as e:
                print("TRex disconnect warning: {}".format(e))
            if not os.environ.get("DISABLE_SYNC") and not os.environ.get("MANUAL_SYNC"):
                try:
                    os.remove(drop_file)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
                try:
                    os.remove(dup_file)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))

        return tOutput


# Entry point used for testing
if __name__ == "__main__":
    driver = QuicDriver("127.0.0.1", 0, 1, "pcap/trex-pcap-files/quic-quic-64.pcap", "100%", 10)
    output = driver.run()
    print(output.toString())
