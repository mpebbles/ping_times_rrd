import rrdtool
import time
from subprocess import STDOUT, check_output

rrdtool.create("test.rrd", "--step", "15", "--start", '0', # every 15 seconds 5 pings are sent
    "DS:ping_avg:GAUGE:30:U:U",
    "RRA:AVERAGE:0.5:1:40",         # every 15 seconds 5 pings are sent
    "RRA:AVERAGE:0.5:4:1440") # 86400/60

secs = 86400
start = time.time()
while time.time() - start < secs:
    loop_time = 15 # seconds
    local_start = time.time()
    try:
        output = str(check_output('ping -c 5 8.8.8.8', stderr=STDOUT, shell=True, timeout=15))
        avg_ping_time = None
        pattern = 'min/avg/max'
        if pattern in output:
            output = output[output.index(pattern):]
            avg_ping_time = float(output[output.index('='):].split('/')[1])
        if avg_ping_time is not None:
            rrdtool.update('test.rrd','N:{}'.format(avg_ping_time))
        else:
            rrdtool.update('test.rrd', 'N:U')
    except Exception as e:
        output = None
        print(e)
        rrdtool.update('test.rrd', 'N:U')
    while time.time() - local_start < loop_time:
        time.sleep(1)


#print(rrdtool.fetch('test.rrd','AVERAGE'))
    rrdtool.graph("mygraph.png", "-a", "PNG", "--end","now","--start","end - 86400s", "--width","1024",
        "--height","512",
	"--slope-mode",
	"--title=Ping Times", "--vertical-label=Ping Time (ms)",
        "DEF:one=test.rrd:ping_avg:AVERAGE",
        "LINE2:one#0000FF:ping_avg"
    )
