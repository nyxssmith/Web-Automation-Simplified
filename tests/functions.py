from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from collections import OrderedDict
from time import sleep
import re
import json
import os


# the actions that tests will use
class actions:

    def get_body_element_by_element_string(self, element_string, driver):
        # get the xpath for an element (fuzzy xpath)
        x_path_element = self.get_xpath_as_string_for_body_element(element_string, driver)

        # x_path_element= "/html/body/div/div[3]/div/div[2]/a"
        print("xpath is", x_path_element)

        # as xpath donest factor in lists, when quesryying it, it can return multple elements,
        # such as all parts of a dropdown
        element_possiblities = driver.find_elements_by_xpath(x_path_element)
        # print(element_possiblities)
        # find the correct element by matching the text of the elements
        for element in element_possiblities:
            # print(element.text)
            if element_string == element.text:
                return element
        # if xpath was invalid (say a placeholder etc) or element not found, return None
        return None

    """
    Take a string and the current driver
    get the html and find all occurences of a string (ex: "Search")
    there could be many index of the string (ex: "Search","Search for...")
    Get all the index's and check that after the string is a < which means its the whole text and not partial
    that way its confirmed to be the correct usage of the string, so if "Search for..." comes before "Search" in the
    html, then it still cuts html at "Search"
    then it takes the whole html up to that index of string
    Then it steps through the html tree
    making a main p-tree, so starts at <body> then goes up and down through the <div> 
    where <div> will add <div> to the p-tree and </div> will remove it
    Then when the html ends where the string was, the remaining p-tree is its xpath,
    since it never gets to close the target elements tags

    """

    def get_xpath_as_string_for_body_element(self, element_string, driver):
        verbose = True

        # get body onwards with no breaks
        src = driver.page_source[driver.page_source.find("</head>") + 7:].replace("\t", "").replace("><",
                                                                                                    ">\n<").replace(
            "> <", ">\n<")
        #print(src)

        src = src.encode('ascii', 'ignore').decode('ascii')
        print(str(src).find(element_string))
        element_string_location = str(src).find(element_string)
        element_string_location_end = str(src)[element_string_location:].find('>') + element_string_location+1
        print(element_string_location)
        print(element_string_location_end)
        print(str(src)[:element_string_location_end])
        #print(str(src).find(element_string))
        #print(str(src)[:str(src).find(element_string)])
        #print(str(src)[:str(src).find(element_string)])
        exit(0)
        # get all index of the occurance of string, in case its search or somehting commong

        # make the element str regex safe
        regex_safe_element_string = element_string.replace("(", "\(").replace(")", "\)").replace(".", "\.").replace("+",
                                                                                                                    "\+").replace(
            ">", "\>").replace("<", "\<").replace("-", "\-")
        # get all indexes when the string shows up, like "search" and "search for"
        list_of_index_of_element_strings = [m.start() for m in re.finditer(regex_safe_element_string, src)]
        # list_of_index_of_element_strings = [m.start() for m in re.finditer('(?=%s)(?!.{1,%d}%s)' % (regex_safe_element_string, len(regex_safe_element_string)-1, regex_safe_element_string), src)]
        # print(list_of_index_of_element_strings)

        # if the list is epmpy, elementi isnt found, so retrun placeholder
        if list_of_index_of_element_strings == []:
            return "html/err"
        # for each possible index
        # print("list of possible indices",list_of_index_of_element_strings)
        for index in list_of_index_of_element_strings:

            # check that right after the target string, is a <
            # if its a space, it could be "search for" rather than "search" which is wrong
            descion_string = src[index:index + len(element_string) + 20]
            # print("d str 1",descion_string)

            descion_string = descion_string.replace("\n", "").replace(" <", "<")
            # if its decied to be correct, retrun corect one
            # print("d str", descion_string)
            # print("index ", index)
            if descion_string[descion_string.find(element_string) + len(element_string):][0] == "<":
                index_of_element_string = index
                break
        # get the html, and cut it off at the string we want
        up_to_element_string = src[:index_of_element_string]
        # split on new lines
        split = up_to_element_string.split("\n")
        split.remove('')

        parent_tree = []
        for line in split:
            if line != '':
                if verbose: print("-=====================")
                if verbose: print("starting p tree", parent_tree)

                # src_dict[counter]["line"] = line
                regex_result_open = re.findall('\<(.*?)\ ', line)

                regex_result_open_ends = re.findall('\<(.*?)>', line)
                # print("rw oepn ends",regex_result_open_ends)

                for result in regex_result_open_ends:
                    # print(result)
                    # print("/" in result)
                    # print(" " in result)
                    if (not ("/" in result)) and (not (" " in result)):
                        # print("keep ",result)
                        regex_result_open.append(result)

                # print("r oepn ends",regex_result_open_ends)

                # add all opened tags to the parent tree
                # dont add input, br or invalid into the parent list, they have been dealt with elsewhere
                for result in regex_result_open:
                    if result != 'input' and result != 'br' and result != 'hr' and (
                            not ((">" or "<") in result) and "--" not in result):
                        parent_tree.append(result)

                regex_result_close = re.findall('</(.*?)\>', line)
                # check if a link was added to the close section, adn rm it, as its a mistake
                for result in regex_result_close:
                    if (line[line.find(result) - 7:line.find(result)] == "href=\"/"):
                        regex_result_close.remove(result)
                    if result == '"' or result == '/"':
                        regex_result_close.remove(result)
                # remove any closed parts from the parent tree
                for result in regex_result_close:
                    if result == parent_tree[-1]:
                        parent_tree.pop()

                if verbose: print("line", line)

                if verbose: print("open", regex_result_open)
                if verbose: print("close", regex_result_close)
                if verbose: print("end p tree", parent_tree)

                if verbose: print("------------------------\n\n")
        if verbose: print("final p treee", parent_tree)

        base_list = ["html"]
        xpath_list = base_list + parent_tree
        if verbose: print("xpath list", xpath_list)

        return "/".join(xpath_list)

    def get_xpath_as_string_for_body_element_old(self, element_string, driver):
        verbose = True

        # get body onwards with no breaks
        src = driver.page_source[driver.page_source.find("</head>") + 7:].replace("\t", "").replace("><",
                                                                                                    ">\n<").replace(
            "> <", ">\n<")

        # get all index of the occurance of string, in case its search or somehting commong

        # make the element str regex safe
        regex_safe_element_string = element_string.replace("(", "\(").replace(")", "\)").replace(".", "\.").replace("+",
                                                                                                                    "\+").replace(
            ">", "\>").replace("<", "\<").replace("-", "\-")
        # get all indexes when the string shows up, like "search" and "search for"
        list_of_index_of_element_strings = [m.start() for m in re.finditer(regex_safe_element_string, src)]
        # list_of_index_of_element_strings = [m.start() for m in re.finditer('(?=%s)(?!.{1,%d}%s)' % (regex_safe_element_string, len(regex_safe_element_string)-1, regex_safe_element_string), src)]
        # print(list_of_index_of_element_strings)

        # if the list is epmpy, elementi isnt found, so retrun placeholder
        if list_of_index_of_element_strings == []:
            return "html/err"
        # for each possible index
        # print("list of possible indices",list_of_index_of_element_strings)
        for index in list_of_index_of_element_strings:

            # check that right after the target string, is a <
            # if its a space, it could be "search for" rather than "search" which is wrong
            descion_string = src[index:index + len(element_string) + 20]
            # print("d str 1",descion_string)

            descion_string = descion_string.replace("\n", "").replace(" <", "<")
            # if its decied to be correct, retrun corect one
            # print("d str", descion_string)
            # print("index ", index)
            if descion_string[descion_string.find(element_string) + len(element_string):][0] == "<":
                index_of_element_string = index
                break
        # get the html, and cut it off at the string we want
        up_to_element_string = src[:index_of_element_string]
        # split on new lines
        split = up_to_element_string.split("\n")
        split.remove('')

        parent_tree = []
        for line in split:
            if line != '':
                if verbose: print("-=====================")
                if verbose: print("starting p tree", parent_tree)

                # src_dict[counter]["line"] = line
                regex_result_open = re.findall('\<(.*?)\ ', line)

                regex_result_open_ends = re.findall('\<(.*?)>', line)
                # print("rw oepn ends",regex_result_open_ends)

                for result in regex_result_open_ends:
                    # print(result)
                    # print("/" in result)
                    # print(" " in result)
                    if (not ("/" in result)) and (not (" " in result)):
                        # print("keep ",result)
                        regex_result_open.append(result)

                # print("r oepn ends",regex_result_open_ends)

                # add all opened tags to the parent tree
                # dont add input, br or invalid into the parent list, they have been dealt with elsewhere
                for result in regex_result_open:
                    if result != 'input' and result != 'br' and result != 'hr' and (
                            not ((">" or "<") in result) and "--" not in result):
                        parent_tree.append(result)

                regex_result_close = re.findall('</(.*?)\>', line)
                # check if a link was added to the close section, adn rm it, as its a mistake
                for result in regex_result_close:
                    if (line[line.find(result) - 7:line.find(result)] == "href=\"/"):
                        regex_result_close.remove(result)
                    if result == '"' or result == '/"':
                        regex_result_close.remove(result)
                # remove any closed parts from the parent tree
                for result in regex_result_close:
                    if result == parent_tree[-1]:
                        parent_tree.pop()

                if verbose: print("line", line)

                if verbose: print("open", regex_result_open)
                if verbose: print("close", regex_result_close)
                if verbose: print("end p tree", parent_tree)

                if verbose: print("------------------------\n\n")
        if verbose: print("final p treee", parent_tree)

        base_list = ["html"]
        xpath_list = base_list + parent_tree
        if verbose: print("xpath list", xpath_list)

        return "/".join(xpath_list)


    # make webdriver object
    def create_driver(self, chrome=False):
        if chrome:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(chrome_options=chrome_options)
        else:
            driver = webdriver.Firefox()
        return driver

    def wait_until_element_by_string_is_not_present(self, element_string, driver):
        print("waiting until element:", element_string, " is not present")
        while (True):
            element = self.get_body_element_by_element_string(element_string, driver)
            if element is not None:
                sleep(1)
            else:
                break

    def wait_until_element_by_string_is_present(self, element_string, driver):
        print("waiting until element:", element_string, " is present")
        while (True):
            element = self.get_body_element_by_element_string(element_string, driver)
            if element is None:
                sleep(1)
            else:
                break


# actions that are test specific
class tests:
    # use shared actions instence
    def __init__(self, test_actions):
        self.actions = test_actions

    # read the test json into orderedDict
    def get_test_list(self, path_to_json):
        test_dict = json.load(open(path_to_json), object_pairs_hook=OrderedDict)
        return test_dict["test"]

    # based on the action field, go to specific action
    def do_test_action(self, driver, element_string, action):
        action_list = []
        if type(action) == list:
            action_list = list(action)
            print("action list", action_list)
            if action_list[0] == "by_id":
                element = driver.find_element_by_id(element_string)
                action = action_list[1]
            elif action_list[0] == "by_string":
                element = self.actions.get_body_element_by_element_string(element_string, driver)
                action = action_list[1]
            elif action_list[0] == "by_xpath":
                element = driver.find_element_by_xpath(element_string)
                action = action_list[1]
            elif action_list[0] == "by_css_path":
                element = None
                action = action_list[1]
            elif action_list[0] == "by_css_selector":
                element = driver.find_elements_by_css_selector(element_string)
                action = action_list[1]
        elif action == "url":
            print("testing url matches")
            self.test_url(driver, element_string)
        elif action == "goto":
            self.test_goto(driver, element_string)
        elif action == "debug" or action == "print":
            self.test_debug_print(element_string)
        elif action == "back":
            driver.back()
        elif element_string == "wait":
            self.test_wait(action)
        else:
            element = self.actions.get_body_element_by_element_string(element_string, driver)

            if type(element) == type([]):
                element = element[0]

            if action == "click":
                self.test_click(driver, element, element_string)
            elif action == "present":
                self.test_present(element, element_string)
            elif action == "keys":
                print("sending keys", action_list[2], "to", element)
                self.test_keys(element, action_list[2])
            elif action == "not_present":
                self.test_not_present(element, element_string)
            elif action == "wait_until_not_present":
                self.actions.wait_until_element_by_string_is_not_present(element_string, driver)
            elif action == "wait_until_present":
                self.actions.wait_until_element_by_string_is_present(element_string, driver)
            elif action == "upload":
                self.test_upload(element, action_list[2])
            else:

                if element_string == "wait":
                    self.test_wait(action)

        print("action is", action, "for element", element_string)

    # test actions

    def test_click(self, driver, element, element_string):
        self.test_present(element, element_string)
        element.click()
        # self.actions.salesforce_safe_click(driver, element)
        print("clicked", element)

    def test_present(self, element, element_string):
        assert element is not None, "Element %r was None, thus non-present" % element_string
        print(element.text, "is present", element)

    def test_not_present(self, element, element_string):
        assert element is None, "Element %r was not None, thus present" % element_string
        print(element_string, " is not present")

    def test_keys(self, element, keys):
        if "CODE:" in keys:
            if "DOWN" in keys:
                element.send_keys(Keys.ARROW_DOWN)
            elif "UP" in keys:
                element.send_keys(Keys.ARROW_UP)
            elif "ENTER" in keys:
                element.send_keys(Keys.ENTER)
        else:
            element.send_keys(keys)

    def test_url(self, driver, element_string):
        assert str(driver.current_url) == str(element_string), "Expected url to be %r but was %r" % (
            element_string, driver.current_url)
        print("url", driver.current_url, " matches expected url ", element_string)

    def test_wait(self, time):
        print("waiting for ", time, "seconds")
        for i in range(1, int(time)):
            sleep(1)
            print(int(time) - i)

    def test_upload(self, element, upload):
        proj_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        files_dir = os.path.join(proj_dir, "files")
        upload_path = os.path.join(files_dir, upload)
        print("uploading ", upload)
        element.send_keys(upload_path)

    def test_goto(self, driver, url):
        print("url is", str(url))
        driver.get(str(url))

    def test_debug_print(self, debug):
        print(debug)
