#!/usr/bin/python3
from threading import Lock
from selenium.webdriver.common.keys import Keys
from Methods import *


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
        self.aggressive = False
        self.driver = None
        self.pages = list()  # Pages
        self.results = list()  # Vulnerabilities results
        self.mutex = Lock()  # Mutex

    def __str__(self):
        output_str = ""
        if self.ip is None:
            output_str += f"IP: Not Specified.\n"
        else:
            output_str += f"IP: {self.ip}\n"
        if self.ip is None:
            output_str += f"PORT: Not Specified.\n"
        else:
            output_str += f"PORT: {self.port}\n"
        if self.url is None:
            output_str += f"URL: Not Specified.\n"
        else:
            output_str += f"URL: {self.url}\n"
        if self.max_pages is None:
            output_str += f"MAXIMUM PAGES: Unlimited.\n"
        else:
            output_str += f"MAXIMUM PAGES: {self.max_pages}\n"
        if self.output is None:
            output_str += f"OUTPUT FILE: Not Specified.\n"
        else:
            output_str += f"OUTPUT FILE: {self.output}\n"            
        if self.username is None:
            output_str += f"USERNAME: Not Specified.\n"
        else:
            output_str += f"USERNAME: {self.username}\n"
        if self.password is None:
            output_str += f"PASSWORD: Not Specified.\n"
        else:
            output_str += f"PASSWORD: {self.password}\n"
        if self.whitelist is None:
            output_str += f"WHITELIST: Not Specified.\n"
        else:
            output_str += f"WHITELIST: {self.whitelist}\n"
        if self.blacklist is None:
            output_str += f"BLACKLIST: Not Specified.\n"
        else:
            output_str += f"BLACKLIST: {self.blacklist}\n"
        output_str += f"RECURSIVE: {self.recursive}\n"
        output_str += f"VERBOSE: {self.verbose}\n"
        output_str += f"AGGRESSIVE: {self.aggressive}"
        return output_str

    @staticmethod
    def submit_form(input_list: list, browser: webdriver.Chrome):
        """
        Function submits the login form
        @param input_list: List of input tags
        @param browser: The session of the request
        @return: The login request
        """
        # The arguments body we want to submit
        elements = list()
        del browser.requests
        url_before = browser.current_url
        for input_tag in input_list:
            if "type" in input_tag.keys() and input_tag['type'] == "hidden":
                continue
            # Using the specified value
            if "name" in input_tag.keys():
                # Only if the input has a name
                element = browser.find_element_by_name(input_tag["name"])
                element.send_keys(input_tag["value"])
                elements.append({"element": element, "name": input_tag["name"], "type": input_tag["type"]})
        if not len(browser.requests):
            # Did not do anything
            try:
                for element in elements:
                    if element["type"] == "text":
                        element["element"].send_keys(Keys.ENTER)  # Sending the form
                if not len(browser.requests):
                    # Did not do anything
                    elements[0]["element"].submit()  # Sending the form
            except Exception as e:
                if not len(browser.requests):
                    # Did not do anything
                    raise e
        for request in browser.requests:
            if request.url == browser.current_url or\
                    url_before == request.url:
                return request
        return [res for res in browser.requests[::-1] if res.response.headers.get("Content-Type") and
                "html" in res.response.headers.get("Content-Type").split(";")[0].lower()][0]


class Page:
    def __init__(self, url: str, status: int, mime_type: str,
                 content: str, request: selenium_request, parent: str):
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
            f"PARENT URL: {self.parent}\n")


class SessionPage(Page):
    def __init__(self, url: str, status: int, mime_type: str,
                 content: str, cookies: list, login: set, request: selenium_request, parent: str):
        super(SessionPage, self).__init__(url, status, mime_type, content, request, parent)
        self.cookies = cookies  # List of dictionaries that webdriver can use
        self.login = login  # Set(The page which the session started from, It's Login form)


class PageResult(Page):
    def __init__(self, page: Page, problem: str, solution: str):
        super(PageResult, self).__init__(page.url, page.status, page.type,
                                         page.content, page.request, page.parent)
        self.problem = problem  # String of problems that were found
        self.solution = solution  # A solution in case of problems


class CheckResults:
    def __init__(self, headline: str, color: str):
        self.headline = headline  # The name of the plugin (xss, rfi, etc..)
        self.color = color  # In case of printing to the screen
        self.page_results = list()  # List of page results
