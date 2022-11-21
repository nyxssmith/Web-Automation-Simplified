FROM ubuntu:20.04

RUN apt update && apt install -y python3 python3-pip

RUN pip3 install selenium

WORKDIR /

COPY test-data /test-data
COPY tests /tests
COPY gen_py_test.py /

RUN python3 gen_py_test.py 

WORKDIR /tests
CMD [ "python3","Run_All_Tests.py" ]