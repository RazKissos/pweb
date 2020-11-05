#!/usr/bin/python3
import mechanize
import http.cookiejar


class Data:
    def __init__(self):
        self.ip = None
        self.url = None
        self.port = None
        self.max_pages = None
        self.folder = None
        self.username = None
        self.password = None
        self.pages = list()  # normal pages
        self.session_pages = list()  # session pages
        self.results = list()  # vulnerabilities results
        self.cookies = http.cookiejar.CookieJar()  # Session cookies
        self.session = mechanize.Browser()  # Session object
        self.session.set_cookiejar(self.cookies)  # Setting the cookies

    def __str__(self):
        return f"IP: {self.ip}\n" \
               f"URL: {self.url}\n" \
               f"PORT: {self.port}\n" \
               f"PAGE MAXIMUM: {self.max_pages}\n" \
               f"OUTPUT FOLDER: {self.folder}\n" \
               f"USERNAME: {self.username}\n" \
               f"PASSWORD: {self.password}"
