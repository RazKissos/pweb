#!/usr/bin/python3
from threading import Lock
import requests


class Data:
    def __init__(self):
        self.ip = None
        self.url = None
        self.port = None
        self.max_pages = None
        self.output = None
        self.username = None
        self.password = None
        self.recursive = False
        self.verbose = True
        self.blacklist = None
        self.whitelist = None
        self.agreement = False
        self.pages = list()  # Pages
        self.results = list()  # Vulnerabilities results
        self.mutex = Lock()  # Mutex

    def __str__(self):
        return (
            f"IP: {self.ip}\n"
            f"URL: {self.url}\n"
            f"PORT: {self.port}\n"
            f"MAXIMUM PAGES: {self.max_pages}\n"
            f"OUTPUT FILE: {self.output}\n"
            f"USERNAME: {self.username}\n"
            f"PASSWORD: {self.password}\n"
            f"RECURSIVE: {self.recursive}\n"
            f"VERBOSE: {self.verbose}\n"
            f"AGREEMENT: {self.agreement}\n"
            f"BLACKLIST: {self.blacklist}\n"
            f"WHITELIST: {self.whitelist}"
        )


class Page:
    def __init__(
        self, url: str, status: int, mime_type: str, content: str, request: requests.Request, parent
    ):
        self.url = url
        self.status = status
        self.type = mime_type
        self.content = content
        self.request = request
        self.parent = parent

    def __str__(self):
        return (
            f"URL: {self.url}\n"
            f"STATUS: {self.status}\n"
            f"CONTENT-TYPE: {self.type}\n"
            f"CONTENT: {self.content}\n"
            f"PARENT URL: {self.parent.url}\n"
        )


class SessionPage(Page):
    def __init__(
        self,
        url: str,
        status: int,
        mime_type: str,
        content: str,
        cookies,
        login: set,
        request: requests.Request,
        parent,
    ):
        super(SessionPage, self).__init__(url, status, mime_type, content, request, parent)
        self.cookies = cookies
        self.login = login  # The page which the session started from


class PageResult(Page):
    def __init__(self, page: Page, problem: str, solution: str):
        super(PageResult, self).__init__(
            page.url, page.status, page.type, page.content, page.request, page.parent
        )
        self.problem = problem  # String of problems that were found
        self.solution = solution  # A solution in case of problems


class CheckResults:
    def __init__(self, headline: str, color: str):
        self.headline = headline  # The name of the plugin (xss, rfi, etc..)
        self.color = color  # In case of printing to the screen
        self.page_results = list()  # List of page results
