from seleniumwire import webdriver, request as selenium_request
import random
import time
from selenium.webdriver.common.keys import Keys

CHECK_STRING = "check"

# ------------------------- Browser methods --------------------------------


def new_browser(data, session_page=None,
                debug: bool = False, interceptor=None) -> webdriver.Chrome:
    """
    Function creates a new browser instance for new session
    @param data: The data object of the program
    @param session_page: In case session, the browser needs the cookies and URL
    @param debug: In case of debugging, True will make the chromium window appear
    @param interceptor:
    @return: Chrome driver object
    """
    if not data.driver:
        # There is no driver file path
        raise Exception("There is no driver file path", "\t")
    options = webdriver.ChromeOptions()
    if not debug:
        # If it's not debug, the chromium will be headless
        options.add_argument("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    try:
        browser = webdriver.Chrome(executable_path=data.driver, options=options)
    except Exception as e:
        # In case of failure, we need to try again
        return new_browser(data, session_page, debug)

    def default_interceptor(request: selenium_request):
        """
        Inner function acts like proxy, it aborts every requests that we don't want
        @param request: The current request
        @return: None
        """
        # Block PNG, JPEG and GIF images
        if request.path.endswith(('.png', '.jpg', '.gif')):
            # Save run time
            request.abort()
    # Setting request interceptor
    if interceptor:
        browser.request_interceptor = interceptor
    else:
        browser.request_interceptor = default_interceptor
    # Setting long timeout
    browser.set_page_load_timeout(60)
    if session_page:
        # In case of session page
        browser.get(session_page.parent)  # Getting parent URL
        for cookie in session_page.cookies:  # Adding cookies
            browser.add_cookie(cookie)
        # Getting the page again, with the cookies
        browser.get(session_page.url)
    return browser


def submit_form(inputs: list, curr_text_input: dict,
                text: str, browser) -> (str, float, list):
    """
    Function submits a specified form
    @param inputs: A list of inputs of action form
    @param curr_text_input: The current text input we are checking
    @param text: The we want to implicate into the current text input
    @param browser: The webdriver object
    @return: The content of the resulted page, the time the action took, the random strings
    """
    # The arguments body we want to submit
    inputs = [dict(input_tag) for input_tag in inputs]  # Deep copy of the list
    check_strings = list()  # List of random strings
    for input_tag in inputs:
        if not input_tag["value"]:
            # If the input tag has no value
            if "name" in input_tag.keys() and input_tag["name"] == curr_text_input["name"]:
                # Only if the input has the current name
                input_tag["value"] = text
            else:
                # If there is no value
                string = get_random_str(browser.page_source)
                input_tag["value"] = string
                check_strings.append(string)
    start = time.time()  # Getting time of normal input
    # Sending the request
    # The elements we want to submit
    elements = list()
    del browser.requests
    for input_tag in inputs:
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
    run_time = time.time() - start
    content = browser.page_source
    return content, run_time, check_strings

# ------------------------------ Helper methods ----------------------------


def get_random_str(content: str) -> str:
    """
    Function generates a random string which is not in the current page
    @param content: The content of the current page
    @return: random string
    """
    while True:
        string = CHECK_STRING + str(random.randint(0, 1000))
        if string not in content:
            return string


def get_text_inputs(form: dict) -> list:
    """
    Function gets the text input names from a form
    @param form: a dictionary of inputs of action form
    @return: list of text inputs
    """
    text_inputs = list()
    for input_tag in form["inputs"]:
        # Using the specified value
        if "name" in input_tag.keys():
            # Only if the input has a name
            if input_tag["type"] and input_tag["type"] == "text":
                text_inputs.append(input_tag)
    return text_inputs


def get_forms(page) -> dict:
    forms = BeautifulSoup(page.content, "html.parser").find_all("form")  # Getting page forms
    for form in forms:
        try:
            # Get the form action (requested URL)
            action = form.attrs.get("action").lower()
            # Get the form method (POST, GET, DELETE, etc)
            # If not specified, GET is the default in HTML
            method = form.attrs.get("method", "get").lower()
            # Get all form inputs
            inputs = []
            for input_tag in form.find_all("input"):
                # Get type of input form control
                input_type = input_tag.attrs.get("type", "text")
                # Get name attribute
                input_name = input_tag.attrs.get("name")
                # Get the default value of that input tag
                input_value = input_tag.attrs.get("value", "")
                # Add everything to that list
                input_dict = dict()
                if input_type:
                    input_dict["type"] = input_type
                if input_name:
                    input_dict["name"] = input_name
                input_dict["value"] = input_value
                inputs.append(input_dict)
            # Setting the form dictionary
            form_details = dict()
            form_details["action"] = action
            form_details["method"] = method
            form_details["inputs"] = inputs
            # Adding the page and it's form to the list
            if len(get_text_inputs(form_details)) != 0:
                # If there are no text inputs, it can't be command injection
                filtered_pages.append((page, form_details))
                if not aggressive:
                    # The user did not specified his agreement
                    return filtered_pages
        except:
            continue
    return filtered_pages