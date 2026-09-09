#!/usr/bin/python

from __future__ import print_function
import yaml
import sys
from optparse import OptionParser

# Config file
CONFIG_FILE = "config.yaml"
# Number of options.runs
RUN = 10


def write_config(configs=[]):
    with open(CONFIG_FILE, "w") as outfile:
        outfile.write(yaml.dump(configs, default_flow_style=False))


# Generate config for all tests
def generate_all(options):
    configs = []
    configs.extend(generate_plain(options, False))
    configs.extend(generate_transit(options, False))
    configs.extend(generate_end(options, False))
    configs.extend(generate_proxy(options, False))
    # Write the entire configuration
    write_config(configs)


def generate_size(size="all"):
    if size == "all":
        configs = [{"size": "max"}, {"size": "min"}]
    elif size == "min":
        configs = [{"size": "min"}]
    elif size == "max":
        configs = [{"size": "max"}]
    else:
        print("Size %s Not Supported Yet" % size)
        sys.exit(-1)
    return configs


def generate_configs(experiments, size):
    configs = []
    # Generate the sizes
    sizes = generate_size(size)
    # Iterate over the experiments
    for experiment in experiments:
        # Iterate over the sizes
        for size in sizes:
            config = experiment.copy()
            config.update(size)
            configs.append(config)
    return configs


# Generate config for plain tests
def generate_plain(options, write=True):
    # Define the experiments
    experiments = []
    if options.pdr:
        experiments.extend(
            [
                {"type": "plain", "experiment": "ipv6", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "plain", "experiment": "ipv4", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
            ]
        )
    if options.mrr:
        experiments.extend(
            [
                {"type": "plain", "experiment": "ipv6", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "plain", "experiment": "ipv4", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
            ]
        )

    for i, experiment in enumerate(experiments):
        if experiment["rate"] == "pdr":
            experiments[i]["start_tx_rate"] = options.start_tx_rate
            if options.line_rate is not None:
                experiments[i]["line_rate"] = options.line_rate

    # Generate configs
    configs = generate_configs(experiments, options.size)
    if not write:
        return configs
    # Write the PLAIN configuration
    write_config(configs)


# Generate config for transit tests
def generate_transit(options, write=True):
    # Define the experiments
    experiments = []
    if options.pdr:
        experiments.extend(
            [
                {"type": "srv6", "experiment": "t_encaps_v6", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "t_encaps_v4", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "t_encaps_l2", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "t_insert_v6", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
            ]
        )
    if options.mrr:
        experiments.extend(
            [
                {"type": "srv6", "experiment": "t_encaps_v6", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "t_encaps_v4", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "t_encaps_l2", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "t_insert_v6", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
            ]
        )
    for i, experiment in enumerate(experiments):
        if experiment["rate"] == "pdr":
            experiments[i]["start_tx_rate"] = options.start_tx_rate
            if options.line_rate is not None:
                experiments[i]["line_rate"] = options.line_rate
    # Generate configs
    configs = generate_configs(experiments, options.size)
    if not write:
        return configs
    # Write the TRANSIT configuration
    write_config(configs)


# Generate config for end tests
def generate_end(options, write=True):
    # Define the experiments
    experiments = []
    if options.pdr:
        experiments.extend(
            [
                {"type": "srv6", "experiment": "end", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_x", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_t", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_b6", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_b6_encaps", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_dx6", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_dx4", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_dx2", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_dt6", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
            ]
        )
    if options.mrr:
        experiments.extend(
            [
                {"type": "srv6", "experiment": "end", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_x", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_t", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_b6", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_b6_encaps", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_dx6", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_dx4", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_dx2", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_dt6", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
            ]
        )

    for i, experiment in enumerate(experiments):
        if experiment["rate"] == "pdr":
            experiments[i]["start_tx_rate"] = options.start_tx_rate
            if options.line_rate is not None:
                experiments[i]["line_rate"] = options.line_rate
    # Generate configs
    configs = generate_configs(experiments, options.size)
    if not write:
        return configs
    # Write the END configuration
    write_config(configs)


# Generate config for proxy tests
def generate_proxy(options, write=True):
    # Define the experiments
    experiments = []
    if options.pdr:
        experiments.extend(
            [
                {"type": "srv6", "experiment": "end_ad6", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_ad4", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
                {"type": "srv6", "experiment": "end_am", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
            ]
        )
    if options.mrr:
        experiments.extend(
            [
                {"type": "srv6", "experiment": "end_ad6", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_ad4", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
                {"type": "srv6", "experiment": "end_am", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
            ]
        )
    for i, experiment in enumerate(experiments):
        if experiment["rate"] == "pdr":
            experiments[i]["start_tx_rate"] = options.start_tx_rate
            if options.line_rate is not None:
                experiments[i]["line_rate"] = options.line_rate
    # Generate configs
    configs = generate_configs(experiments, options.size)
    if not write:
        return configs
    # Write the PROXY configuration
    write_config(configs)


def generate_quic(options, write=True):
    # Define the experiments
    experiments = []
    if options.pdr:
        experiments.extend(
            [
                {"type": "quic", "experiment": "quic", "rate": "pdr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "lb_dlr": options.lb_dlr, "ndr_window": options.ndr_window},
            ]
        )
    if options.mrr:
        experiments.extend(
            {"type": "quic", "experiment": "quic", "rate": "mrr", "run": options.runs, "tx_port": options.tx_port, "rx_port": options.rx_port, "mrr_rate": options.mrr_rate},
        )

    for i, experiment in enumerate(experiments):
        if experiment["rate"] == "pdr":
            experiments[i]["start_tx_rate"] = options.start_tx_rate
            if options.line_rate is not None:
                experiments[i]["line_rate"] = options.line_rate
    # Generate configs
    configs = generate_configs(experiments, options.size)
    if not write:
        return configs
    # Write the PROXY configuration
    write_config(configs)


# Parse options
def generate():
    # Init cmd line parse
    parser = OptionParser()
    parser.add_option("-t", "--type", dest="type", type="string", default="plain", help="Test type {plain|transit|end|proxy|all}")
    parser.add_option("-s", "--size", dest="size", type="string", default="all", help="Size type {max|min|all}")
    parser.add_option("--runs", dest="runs", type="int", default=RUN, help="Number of options.runs")
    parser.add_option("--tx_port", dest="tx_port", type="int", default=0, help="Tx port")
    parser.add_option("--rx_port", dest="rx_port", type="int", default=1, help="Rx port")
    parser.add_option("--lb_dlr", dest="lb_dlr", type="float", default=0.995, help="PDR Lower bound for delivery ratio")
    parser.add_option("--mrr_rate", dest="mrr_rate", type="string", default="100%", help="MRR rate as string (100%)")
    parser.add_option("--ndr_window", dest="ndr_window", type="float", default=100, help="Window for NDR(epsilon) in pps")
    parser.add_option("--start_tx_rate", dest="start_tx_rate", type="float", default=1.0, help="Starting tx rate for NDR in pps")
    parser.add_option("--line_rate", dest="line_rate", type="float", default=None, help="Line rate for NDR in pps")
    parser.add_option("--no_mrr", dest="mrr", default=True, action="store_false", help="Enable MRR")
    parser.add_option("--no_pdr", dest="pdr", default=True, action="store_false", help="Enable PDR")

    # Parse input parameters
    (options, args) = parser.parse_args()
    # Run proper generator according to the type
    if options.type == "plain":
        generate_plain(options, True)
    elif options.type == "transit":
        generate_transit(options, True)
    elif options.type == "end":
        generate_end(options, True)
    elif options.type == "proxy":
        generate_proxy(options, True)
    elif options.type == "all":
        generate_all(options)
    elif options.type == "quic":
        generate_quic(options, True)
    else:
        print("Type %s Not Supported Yet" % options.type)


if __name__ == "__main__":
    generate()
