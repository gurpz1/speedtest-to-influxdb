from config import InfluxDB

import subprocess
import logging
import json
import sys
import argparse
import time

from influxdb_client import InfluxDBClient


def setup_args(parser):
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug messages"
    )
    parser.set_defaults(cmd="default")

    subparsers = parser.add_subparsers()
    loop_parser = subparsers.add_parser(
        "loop",
        help="Loop test"
    )
    loop_parser.set_defaults(cmd="loop")
    loop_parser.add_argument(
        "--timeout",
        help="Timeout period (s)",
        type=int,
        default=1800  # default once every 30 mins
    )


def collect_speed_test_results():
    cmd = "speedtest"
    if sys.platform == "win32":
        cmd = "C:/Users/gurpals/Downloads/speedtest.exe"
    logging.info("Running Speedtest CLI")
    output = subprocess.run([
        cmd,
        "--accept-license",
        "--accept-gdpr",
        "-f",
        "json"
    ], capture_output=True)

    try:
        output.check_returncode()
        results = json.loads(output.stdout)
        logging.debug("Raw results from Speedtest:")
        logging.debug(json.dumps(results, indent=4))
        return results
    except Exception:
        logging.fatal("Unable to execute SpeedTest")
        logging.fatal("Check CLI is running correctly and able to access the internet")
        sys.exit(1)


def format_for_influx(results):
    influx_data = [
        {
            'measurement': 'ping',
            'time': results['timestamp'],
            'fields': {
                'jitter': results['ping']['jitter'],
                'latency': results['ping']['latency']
            }
        },
        {
            'measurement': 'download',
            'time': results['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': results['download']['bandwidth'],
                'bytes': results['download']['bytes'],
                'elapsed': results['download']['elapsed']
            }
        },
        {
            'measurement': 'upload',
            'time': results['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': results['upload']['bandwidth'],
                'bytes': results['upload']['bytes'],
                'elapsed': results['upload']['elapsed']
            }
        },
        {
            'measurement': 'packetLoss',
            'time': results['timestamp'],
            'fields': {
                'packetLoss': int(results['packetLoss']) if "packetLoss" in results else 0
            }
        }
    ]

    logging.debug("Writing the following to Influx")
    logging.debug(json.dumps(influx_data, indent=4))
    return influx_data


def write_data_to_influx(data_to_write):
    influx_client = InfluxDBClient(url=InfluxDB.url, token=InfluxDB.token, org=InfluxDB.org)
    logging.info("Writing to InfluxDB")
    write_client = influx_client.write_api()
    write_client.write(bucket=InfluxDB.bucket, record=data_to_write)

    write_client.__del__()
    influx_client.__del__()


def main(parsed_args):
    while 1:
        results = collect_speed_test_results()
        data_to_write = format_for_influx(results)
        write_data_to_influx(data_to_write)
        if parsed_args.cmd != "loop":
            break
        logging.info(f"Sleeping for {parsed_args.timeout} seconds.")
        time.sleep(parsed_args.timeout)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Handy utility to load speedtest data to influxdb")
    setup_args(arg_parser)
    args = arg_parser.parse_args()

    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s'
                        )
    main(args)
