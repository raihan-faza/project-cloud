import time

balance = 10000


def cut_balance(balance):
    stop = False
    while stop != True:
        time.sleep(60)
        balance = balance - 100

    return


def read_log(container_log: str):
    log = open(container_log).read().replace("\n", "").split(";")
    log.remove('')
    return log


read_log("log_containerid.txt")
