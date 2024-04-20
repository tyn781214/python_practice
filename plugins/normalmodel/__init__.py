import psutil

def MemInfo():
    memory = psutil.virtual_memory()
    total = round(memory.total / 1024.0 / 1024.0, 2)
    used = round(memory.used / 1024.0 / 1024.0, 2)
    free = round(memory.free / 1024.0 / 1024.0, 2)
    percent = memory.percent

    info = f'''
=== MemoryInfo ===
total memory: {total} MB;
used: {used} MB; free: {free} MB
usage: {percent}%
    '''.strip()

    return info

def CpuInfo():
    count = psutil.cpu_count(logical=False)
    usage = psutil.cpu_percent(interval=0.5, percpu=True)
    times = psutil.cpu_times_percent(percpu=False)

    info = f'''
=== CpuInfo ===
total core: {count};
usage(avg): {round(sum(usage) / len(usage), 2)}%
usage(per): {", ".join([str(i) + "%" for i in usage])}
[user: {times.user}%; system: {times.system}%; idle: {times.idle}%]
    '''.strip()

    return info

def DiskInfo():
    disk = psutil.disk_usage("C:\\")

    info = f'''
=== DiskInfo ===
total: {round(disk.total / 1024 / 1024 / 1024, 2)} GB
used: {round(disk.used / 1024 / 1024 / 1024, 2)} GB
usage: {disk.percent}%
    '''.strip()

    return info


if __name__ == '__main__':
    print(DiskInfo())