import psutil
import socket
import threading
import time
import json
import sys
import signal
import argparse
import statsd

options = {}


class ExportServer(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name
        self.shutdown_flag = threading.Event()

    def run(self):
        print('Thread #%s started' % self.ident)
        while not self.shutdown_flag.is_set():
            time.sleep(1)
            stats_client.on_message(get_proc_list(self._name))
        print('Thread #%s stopped' % self.ident)


def get_proc_list(host_name):
    build_message = []
    msg_size = 0
    proc_len = 0
    for p in psutil.process_iter(attrs=['pid', 'memory_info']):
        try:
            proc = {}
            proc['host'] = host_name
            proc['pid'] = p.pid
            proc['mem'] = p.info['memory_info'].rss

            proc_len = len(str(proc).encode('utf8'))
            msg_size += proc_len
            if (msg_size < 1500 - proc_len):
                build_message.append(proc)
            else:
                return build_message

        except Exception as e:
            if type(e) == psutil.AccessDenied(Exception):
                pass
        # print(build_message) ## Testing
    return build_message


class StatsClient(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        global c
        c = statsd.StatsClient('localhost', 8125, 'statsclient')

        while True:
            pass

    def on_message(self, message):
        try:
            for proc in message:
                name = '%s.%d' % (proc['host'], proc['pid'])
                c.gauge(name, proc['mem'], rate=1, delta=False)

        except Exception as ex:
            print('Could not parse the message: %s' % str(ex))


def create_hosts(numHosts):
    host_list = []
    global start_time
    for host in range(numHosts):
        host_name = 'host{}'.format(host)
        host_name = ExportServer(host_name)
        host_name.start()
        host_list.append(host_name)
    start_time = time.time()
    print('Hosts created:', numHosts)

    return host_list


def destroy_hosts(hosts):
    for host in hosts:
        host.shutdown_flag.set()
        host.join()


def service_shutdown(signum, frame):
    end_time = time.time()
    if end_time - start_time > 5:
        print(' <== Caught signal %d' % signum)
        raise ServiceExit
    else:
        print(' Please wait for threads to initialize so they can exit gracefully.')


class ServiceExit(Exception):
    pass


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    parser = argparse.ArgumentParser(
        prog='host-exporter', description='Collect and process information to a metrics backend.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--hosts', help='The number of hosts to generate.', default=1, type=int, dest='hosts')

    args = parser.parse_args()
    try:
        options['num_hosts'] = args.hosts or raise_exception(
            'INVALID HOST NUMBER')
    except Exception as ex:
        print('Could not parse the arguments: %s' % str(ex))
        sys.exit(1)

    stats_client = StatsClient()
    stats_client.start()

    try:
        h = create_hosts(options['num_hosts'])

        while True:
            time.sleep(0.5)

    except ServiceExit:
        destroy_hosts(h)
        print('Service terminated.')
