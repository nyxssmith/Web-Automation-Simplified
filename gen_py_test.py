import os

test_data = os.listdir("test-data")
tests = os.listdir("tests")

py_tests = []
for py_test in tests:
    py_tests.append(py_test.replace(".py",".json"))

print(py_tests)
print(test_data)

placeholder_python = """
from functions import actions,tests

test_actions = actions()
test_tests = tests(test_actions)


driver = test_actions.create_driver(chrome=False)
test_list = test_tests.get_test_list("CWD/test-data/JSONFILE")
for item in test_list:
    element = list(item.keys())[0]
    action = item[list(item.keys())[0]]
    test_tests.do_test_action(driver,element,action)
driver.close()
"""
test_data.remove("test-template.json")


for test in test_data:
    print(("Test_"+test.replace("-","_")[0].upper()+test.replace("-","_")[1:]).replace(".json",".py"))
    test_name = (("Test_"+test.replace("-","_")[0].upper()+test.replace("-","_")[1:]).replace(".json",".py"))
    print(test_name in py_tests)
    python_content = placeholder_python.replace("JSONFILE",test).replace("CWD",os.getcwd())
    with open("tests/"+test_name,"w")as test_python:
        test_python.write(python_content)
