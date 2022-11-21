from functions import actions,tests
import os
import time

# wait 10s for chrome startup
time.sleep(10)


test_actions = actions()
test_tests = tests(test_actions)

list_of_tests = os.listdir(os.path.join("..","test-data"))
try:
    list_of_tests.remove(".DS_Store")
    list_of_tests.remove("test-template.json")
except:
    pass
print(list_of_tests)
passed = []
failed = []
for test in list_of_tests:

    cur_step = dict()
    cur_step["step"] = -1
    cur_step["info"] = None

    try:
        print("\n==============================\nRunning test:",test.replace(".json",""))
        json_path = os.path.join(os.path.join("..","test-data"),test)

        driver = test_actions.create_driver()
        #test_actions.login_to_typecore(driver)
        test_list = test_tests.get_test_list(json_path)
        print("test list",test_list)
        for item in test_list:
            print("start item")
            cur_step["step"] = test_list.index(item)+1
            cur_step["info"] = "Expected "+str(list(item.keys())[0])+" to be/type "+str(list(item.values())[0])
            element = list(item.keys())[0]
            action = item[list(item.keys())[0]]
            test_tests.do_test_action(driver, element, action)
        driver.close()
        print("==============================")
        passed.append(test.replace(".json",""))
    except Exception as e:
        print("Test Failed with Errors")
        failed.append(test.replace(".json","")+":\nOn step "+str(cur_step["step"])+" which was "+str(cur_step["info"])+"\n"+str(e))
        driver.close()


with open("../test_output.txt","w")as out:

    out_str = ""
    print("\n"+str(len(passed))+" test passed")
    out_str+="\n"+str(len(passed))+" test passed"

    for test in passed:
        test_name = (("Test_"+test.replace("-","_")[0].upper()+test.replace("-","_")[1:]).replace(".json",".py"))
        print(test_name)
        out_str += "\n" +test_name
    print("\n"+str(len(failed))+" test failed")
    out_str += "\n" +"\n"+str(len(failed))+" test failed"
    for test in failed:
        test_name = (("Test_"+test.replace("-","_")[0].upper()+test.replace("-","_")[1:]).replace(".json",".py"))
        print(test_name)
        out_str+="\n"+test_name
    out.write(out_str)
    out.close()