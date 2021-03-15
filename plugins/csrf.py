#!/usr/bin/python3
from colors import COLOR_MANAGER
import Classes
import Methods
import OutputManager

# Consts:
COLOR = COLOR_MANAGER.rgb(0, 255, 200)
OUTSIDE_URL = "https://google.com"

# Global variables:
current_referer = None
problem_get = Classes.CheckResult("The use of GET request when submitting the form might be vulnerable.",
                                  "You can change the method of the request to POST.")
problem_referer = Classes.CheckResult("The form submission did not detect the 'Referer' header,"
                                      " which was not the same page that has the vulnerable form.",
                                      "You can validate the 'Referer' header of the request,"
                                      " so it will perform only actions from the current page.")


def check(data: Classes.Data):
    """
    Function checks the website for CSRF
    @param data: The data object of the program
    @return: None
    """
    csrf_results = Classes.CheckResults("CSRF", COLOR)
    try:
        data.mutex.acquire()
        pages = data.pages  # Achieving the pages
        aggressive = data.aggressive
        data.mutex.release()
        for page in pages:
            # Getting the forms of each page
            forms = filter_forms(page)
            if forms and not aggressive:
                # The user did not specified his agreement
                # and there is a vulnerable page
                csrf_results.warning = "The plugin check routine requires injecting text boxes," \
                                            " read about (-A) in our manual and try again."
                break
            for form in forms:
                try:
                    csrf(page, form, data)
                except Exception:
                    continue
    except Exception as e:
        csrf_results.error = "Something went wrong..."

    csrf_results.results.append(problem_get)
    csrf_results.results.append(problem_referer)
    csrf_results.conclusion = "The best way to prevent CSRF vulnerability is to use CSRF Tokens, " \
                              "read more about it in: 'https://portswigger.net/web-security/csrf/tokens'."
    data.mutex.acquire()
    data.results_queue.put(csrf_results)  # Adding the results to the queue
    data.mutex.release()


def filter_forms(page: Classes.Page) -> list:
    """
    Function filters the pages that has an action form
    @param page: The current page
    @return: List of forms
    """
    filtered_forms = list()
    if "html" in page.type.lower() and type(page) is Classes.SessionPage:
        # The only thing we need is a HTML session page with a form
        for form in Methods.get_forms(page.content):
            # Adding the page and it's form to the list
            filtered_forms.append(form)
    return filtered_forms


def csrf(page: Classes.SessionPage, form: dict, data: Classes.Data):
    """
    Function checks the page for csrf
    @param page: The current page
    @param form: The page's action form
    @param data: The data object of the program
    @return: None
    """
    page_result = Classes.PageResult(page, f"Action form: '{form['action']}'")
    # Checking for csrf tokens
    request_headers = page.request.headers
    response_headers = page.request.response.headers
    if response_headers.get("Set-Cookie") and \
            ("SameSite=Strict" in response_headers.get("Set-Cookie") or
             "csrf" in response_headers.get("Set-Cookie")) or request_headers.get("X-Csrf-Token"):
        # Found a SameSite or csrf token in response header
        return
    # Setting new browser
    browser = Methods.new_browser(data, page, interceptor=interceptor)
    token = False
    try:
        for new_form in Methods.get_forms(browser.page_source):
            if new_form["action"] != form["action"]:
                # Not the same form
                continue
            for input_tag in form["inputs"]:
                # Using the specified value
                if "name" in input_tag.keys() and input_tag["value"]:
                    # Only if the input has a name and a value
                    for new_input_tag in new_form["inputs"]:
                        if "name" in new_input_tag.keys() and new_input_tag["name"] == input_tag["name"]:
                            # If the input tags have the same name
                            if new_input_tag["value"] != input_tag["value"]:
                                # If the input tags have different values
                                token = True
                                break
                    if token:
                        # No need to look for another input tag
                        break
                break  # There is only one fitting form
    except Exception:
        pass
    browser.quit()
    if token:
        # Found a csrf token
        return
    # Join the url with the action (form request URL)
    if form["method"] == "get":
        # Dangerous by itself
        Methods.add_page_result(problem_get, page_result, ", ")
    # Getting normal content
    normal_content = get_response(form["inputs"], page.url, data, page)
    # Getting redirected content
    referer_content = get_response(form["inputs"], OUTSIDE_URL, data, page)
    if normal_content == referer_content:
        # Does not filter referer header
        Methods.add_page_result(problem_referer, page_result, ", ")
    elif page.parent:
        # Getting local redirected content
        referer_content = get_response(form["inputs"], page.parent.url, data, page)
        if normal_content == referer_content:
            # Does not filter referer header
            Methods.add_page_result(problem_referer, page_result, ", ")


def get_response(inputs: list, referer: str, data: Classes.Data, page) -> str:
    """
    Function submits a specified form and gets the result content
    @param inputs: A list of inputs of action form
    @param referer: A specified referer address
    @param data: The data object of the program
    @param page: The current page
    @return: The content of the resulted page
    """
    content = ""
    try:
        # Sending the request
        global current_referer
        current_referer = referer
        browser = Methods.new_browser(data, page, interceptor=interceptor)
        check_strings = list()
        inputs = [dict(input_tag) for input_tag in inputs]
        for input_tag in inputs:
            # Using the specified value
            if input_tag in Methods.get_text_inputs(inputs):
                # Only if the input has a name
                if not input_tag["value"]:
                    # There is no value to the input tag
                    check_string = Methods.get_random_str(browser.page_source)
                    check_strings.append(check_string)
                    input_tag["value"] = check_string
        content, run_time = Methods.submit_form(inputs, browser, data)
        current_referer = None
        content = browser.page_source
        browser.quit()
        for string in check_strings:
            # In case that the random string is in the content
            content = content.replace(string, "")
        # In case of referrers in content
        content = content.replace(page.url, "").replace(OUTSIDE_URL, "")
        if page.parent:
            content = content.replace(page.parent.url, "")
    except Exception as e:
        pass
    finally:
        return Methods.remove_forms(content)


def interceptor(request):
    """
    Function acts like proxy, it changes the requests header
    @param request: The current request
    @return: None
    """
    # Block PNG, JPEG and GIF images
    global current_referer
    if request.path.endswith(('.png', '.jpg', '.gif')):
        # Save run time
        request.abort()
    elif current_referer:
        # In case of referer specified
        del request.headers['Referer']  # Remember to delete the header first
        request.headers['Referer'] = current_referer  # Spoof the referer
