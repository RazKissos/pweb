#!/usr/bin/python3
from threading import Lock
from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys


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
        self.driver = None
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
            f"WHITELIST: {self.whitelist}")

    def new_browser(self) -> [webdriver.Chrome]:
        """
        Function creates new browser instance for new session
        @param self: The data object of the program
        @return: Chrome driver object
        """
        if not self.driver:
            # There is no driver file path
            raise Exception("There is no driver file path", "\t")
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return webdriver.Chrome(executable_path=self.driver, options=options)

    @staticmethod
    def submit_form(form_details: dict, browser: webdriver.Chrome):
        """
        Function submits the login form
        @param form_details: Dictionary of the form details
        @param browser: The session of the request
        @return: The login request
        """
        # The arguments body we want to submit
        elements = list()
        requests_before = browser.requests
        url_before = browser.current_url
        before_submit = [browser.current_url, browser.page_source]
        for input_tag in form_details["inputs"]:
            # Using the specified value
            if "name" in input_tag.keys():
                # Only if the input has a name
                element = browser.find_element_by_name(input_tag["name"])
                element.send_keys(input_tag["value"])
                elements.append({"element": element, "name": input_tag["name"], "type": input_tag["type"]})
        if before_submit[0] == browser.current_url and \
                browser.page_source == before_submit[1]:
            # Did not do anything
            # Sending the form
            for element in elements:
                if element["type"] != "text":
                    element["element"].click()
            if before_submit[0] == browser.current_url and \
                    browser.page_source == before_submit[1]:
                # Did not do anything
                for element in elements:
                    if element["type"] == "text":
                        element["element"].send_keys(Keys.ENTER)  # Sending the form
                if before_submit[0] == browser.current_url and \
                        browser.page_source == before_submit[1]:
                    # Did not do anything
                    elements[0]["element"].submit()  # Sending the form
        requests_after = [res for res in browser.requests[len(requests_before)::-1]]
        for request in requests_after:
            if request.url == browser.current_url or\
                    url_before == request.url:
                return request
        return [res for res in browser.requests[::-1] if res.response.headers.get("Content-Type") and
                "html" in res.response.headers.get("Content-Type").split(";")[0].lower()][0]


class Page:
    def __init__(self, url: str, status: int, mime_type: str,
                 content: str, request, parent):
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
            f"PARENT URL: {self.parent.url}\n")


class SessionPage(Page):
    def __init__(self, url: str, status: int, mime_type: str,
                 content: str, cookies: list, login: set, request, parent):
        super(SessionPage, self).__init__(url, status, mime_type, content, request, parent)
        self.cookies = cookies  # List of dictionaries that webdriver can use
        self.login = login  # The page which the session started from


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
