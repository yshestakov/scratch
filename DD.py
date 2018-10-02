from threading import Thread
from subprocess import PIPE, Popen
from time import time


class MyThread(Thread):
    def __init__(self, file_name, file_size, count, t_number):
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
        except:
            exit(1)


def check_disk(min_size):
    try:
        disks = []
        disks_list = Popen(["df", "-lBM", "--output=source,avail"], stdout=PIPE)

        for line in disks_list.stdout.readlines():
            if line.startswith("/dev"):
                size = int(line.strip().split()[-1].replace('M', ''))
                if size > min_size:
                    disks.append(line.strip().split()[0])
    except:
        raise exit(1)

    return disks


def create_files(file_name, file_size, count):
    try:
        for i in range(1, count+1):
            with open(file_name + str(i), "wb") as file:
                file.write(b"\0" * 1024 * 1024 * file_size)
    except:
        exit(1)


def main():
    count = 10
    disk_min = 500
    file_size = 10
    file_name = 'file'

    check_disk(disk_min)
    create_files(file_name, file_size, count)

    threads = []
    for i in range(1, count+1):
        threads.append(MyThread(file_name + str(i), file_size, count, i))

    for t in threads:
        t.start()


if __name__ == "__main__":
    main()
