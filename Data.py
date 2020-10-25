#!/usr/bin/python3
import mechanize
import http.cookiejar


class Data:
    def __init__(self, ip="127.0.0.1", address="",
                 username=None, password=None,
                 max_pages=-1, port=80, all_ports=False, output_folder=None):
        """
        :param url: the address of the target
        :param username: the user's username
        :param password: the user's password
        :param max_pages: the maximum pages amount
        :param port: the port of the target
        :param folder: the folder of the output files
        """
        self.ip = ip
        self.address = address
        self.port = port
        self.all_ports = all_ports
        self.max_pages = max_pages
        self.folder = output_folder
        self.username = username
        self.password = password
        self.pages = list()  # normal pages
        self.session_pages = list()  # session pages
        self.results = list()  # vulnerabilities results
        self.cookies = http.cookiejar.CookieJar()  # Session cookies
        self.session = mechanize.Browser()  # Session object
        self.session.set_cookiejar(self.cookies)  # Setting the cookies
    
    def __str__(self):
        return f"""{self.ip}\n{self.address}\n{self.port}\n{self.all_ports}\n{self.max_pages}\n{self.folder}\n{self.username}\n{self.password}"""
