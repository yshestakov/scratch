from threading import Thread
from subprocess import PIPE, Popen
from time import time

from logging import basicConfig, info, ERROR, error
basicConfig(level=ERROR, format="%(asctime)s - [%(levelname)s] [%(threadName)s]"
                                " (%(module)s:%(lineno)d) %(message)s", filename="errors.log")


'''
  Define a Thread-class to run the tasks in parallel.
  Vars description are available in their input prompt
'''

class MyThread(Thread):
    def __init__(self, file_name, file_size, count, t_number):
        info("Initializing thread %s to execute..." % t_number)
        Thread.__init__(self)
        super(MyThread, self).__init__()
        self.name = file_name
        self.size = str(file_size) + "M"
        self.count = str(count)
        self.number = t_number

    def run(self):
        try:
            start_time = time()
            Popen(["dd", "if=/dev/urandom", "bs="+self.size,
                   "count="+self.count, "of="+self.name], stderr=PIPE)

            print("Time to execute thread #%s: " % self.number, time() - start_time)
        except Exception:
            error("Oh, no! You gotta check the input values and/or run-function")
            exit(1)


def check_disk(min_size):
    try:
        disks = []
        disks_list = Popen(["df", "-lBM", "--output=source,avail"], stdout=PIPE)
        info("Collecting info about disks and available space are completed!")

        for line in disks_list.stdout.readlines():
            if line.startswith("/dev"):
                size = int(line.strip().split()[-1].replace('M', ''))
                if size > min_size:
                    disks.append(line.strip().split()[0])
    except Exception:
        error("Oh, no! Collecting disks info failed!")
        raise exit(1)

    return disks


def create_files(file_name, file_size, count):
    try:
        for i in range(1, count+1):
            with open(file_name + str(i), "wb") as file:
                file.write(b"\0" * 1024 * 1024 * file_size)
                info("File %s has been created successfully" % file_name+str(i))
    except Exception:
        error("Oh, no! Files couldn't be created!")
        exit(1)


def main():
    count = int(input("Please, enter the number of threads: "))
    disk_min = int(input("Please, enter the minimum size of disk free space: "))
    file_size = int(input("Please, enter the size of files to create: "))
    file_name = input("Please, enter a prefix for file names: ")

    check_disk(disk_min)
    create_files(file_name, file_size, count)

    threads = []
    for i in range(1, count+1):
        threads.append(MyThread(file_name + str(i), file_size, count, i))

    info("Let's go with multi-threading!")
    for t in threads:
        t.start()


if __name__ == "__main__":
    main()
