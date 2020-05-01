
from functions import actions,tests

test_actions = actions()
test_tests = tests(test_actions)


driver = test_actions.create_driver(chrome=False)
test_list = test_tests.get_test_list("/home/nick/Git/Web-Automation-Simplified/test-data/microcenter_home_page.json")
for item in test_list:
    print("item",item)
    element = list(item.keys())[0]
    action = item[list(item.keys())[0]]
    test_tests.do_test_action(driver,element,action)
driver.close()
