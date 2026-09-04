#!/usr/bin/python

from __future__ import print_function
import sys
import os

# We need to add tester modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../tester"))

from NoDropRateSolver import *
from TrexPerf import TrexExperimentFactory
from QuicPerf import QuicExperimentFactory
from config_parser import ConfigParser

# Trex server
TREX_SERVER = "127.0.0.1"
# TX port
TX_PORT = 0
# RX port
RX_PORT = 1
# Duration of a single RUN (time to get a sample)
DURATION = 10
# pcap location
PCAP_HOME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../pcap/trex-pcap-files")
# Define the namber of samples for a given PDR
SAMPLES = 1
# Starting tx rate
STARTING_TX_RATE = 100.0
# NDR window
NDR_WINDOW = 500.0
# Lower bound for delivery ratio
LB_DLR = 0.995


# Realizes a PDR experiment
class PDR(object):
    # Run a PDR experiment using the config provided as input
    @staticmethod
    def run(config):
        results = []
        # We collect run PDR values and we return them
        for iteration in range(0, config.run):
            print("PDR %s-%s Run %s" % (config.type, config.experiment, iteration))
            # At first we create the experiment factory with the right parameters
            if config.type == "quic":
                factory = QuicExperimentFactory(TREX_SERVER, config.tx_port, config.rx_port, "%s/%s.pcap" % (PCAP_HOME, ConfigParser.get_packet(config)), SAMPLES, DURATION)
            else:
                factory = TrexExperimentFactory(TREX_SERVER, config.tx_port, config.rx_port, "%s/%s.pcap" % (PCAP_HOME, ConfigParser.get_packet(config)), SAMPLES, DURATION)
            # Then we instantiate the NDR solver with the above defined parameters
            ndr = NoDropRateSolver(STARTING_TX_RATE, config.line_rate, config.ndr_window, config.lb_dlr, RateType.PPS, factory)
            ndr.solve()
            # Once finished let's collect the results
            results.append(ndr.getSW()[0])
        return results
