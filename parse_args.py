#!/usr/bin/python3
import argparse
import colors
import sys

COLOR_MANAGER = colors.Colors()


def validIPAddress(IP):
    """
      :type IP: str
      :rtype: str
      """

    def isIPv4(s):
        try:
            return str(int(s)) == s and 0 <= int(s) <= 255
        except:
            return False

    if IP.count(".") == 3 and all(isIPv4(i) for i in IP.split(".")):
        return True
    return False


def parse_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--ip",
        default="127.0.0.1",
        type=str,
        help="Enter the ip of the host server. (Not necessary if argument <url> is specified)",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=80,
        type=int,
        help="Specify a known port on which a web server is serving, if not specified, default port would be 80.\n You can use flag -P to force an all-port scan.",
    )
    parser.add_argument(
        "-P",
        "--ALL_PORTS",
        action="store_true",
        help="Specify this flag when port isn't known and you wish to scan all ports.",
    )
    parser.add_argument(
        "-u",
        "--url",
        default="",
        type=str,
        help="Instead of specifying an ip address you can specifically specify a url.",
    )
    parser.add_argument(
        "-n",
        "--number_of_pages",
        default=None,
        type=int,
        help="Limit the amount of pages checked to a specific amount.",
    )
    parser.add_argument(
        "-L",
        "--login",
        default=list(),
        type=list,
        nargs=2,
        help="Specify a username and password to be used in any login form on the website.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="",
        type=str,
        help="Specify a directory path in which the output will be stored.",
    )
    args = parser.parse_args()

    to_ret = dict()
    if type(args.login) != None:
        if len(args.login) == 2:
            creds = {
                "username": string(args.login[0]),
                "password": string(args.login[1]),
            }
            # Username. Password.
        else:
            creds = dict()
    else:
        creds = dict()

    if not validIPAddress(args.ip):
        print(
            COLOR_MANAGER.BRIGHT_YELLOW
            + "[!] Invalid IP address, using default localhost."
            + COLOR_MANAGER.ENDC
        )
        args.ip = "127.0.0.1"

    if args.url == "":
        # IP will be used.
        to_ret = {
            "ip": args.ip,
            "port": args.port,
            "ALL_PORTS": args.ALL_PORTS,
            "IS_URL": False,
            "url": "",
            "num_of_pages": args.number_of_pages,
            "credentials": creds,
            "output": args.output,
        }
    else:
        # URL will be used.
        to_ret = {
            "ip": "",
            "port": args.port,
            "ALL_PORTS": args.ALL_PORTS,
            "IS_URL": True,
            "url": args.url,
            "num_of_pages": args.number_of_pages,
            "credentials": creds,
            "output": args.output,
        }
    print(to_ret)  # for debugging purposes.
    return to_ret
