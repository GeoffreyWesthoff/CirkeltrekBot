import json
import multiprocessing
import subprocess
from datetime import datetime
from math import floor, ceil
from os import chdir, getcwd
from time import time

import requests

OKGREEN = '\033[92m'
ENDC = '\033[0m'
WARNING = '\033[93m'
OKBLUE = '\033[94m'

threads = []


class App:
    def __init__(self):
        self.socket = None
        with open('logo.txt', 'r') as logo:
            print(logo.read())
        print(f'{OKGREEN}Welcome to Shardaux{ENDC}')
        try:
            config = json.load(open('cluster_settings.json'))
            token = config.get('token')
            cluster_count = config.get('clusters')
            path = config.get('path')
        except FileNotFoundError:
            print(f'{WARNING}Configuration not found!\n'
                  f"Let's set this up shall we?{ENDC}\n\n")
            token = input(f'{OKBLUE}Enter your bot token!{ENDC}\n')
            cluster_count = input(f'{OKBLUE}Now choose how many clusters you want to run!{ENDC}\n')
            if not cluster_count:
                cluster_count = 1
            want_save = input(f'{OKGREEN}Everything set, do you want to save?{ENDC}')
            if want_save.startswith('y'):
                with open('example_cluster_settings.json', 'w') as f:
                    settings = json.dumps({"token": token, "clusters": cluster_count})
                    f.write(settings)
        gateway_headers = {"Authorization": f"Bot {token}"}
        gateway = requests.get('https://discordapp.com/api/gateway/bot', headers=gateway_headers)
        gateway_j = gateway.json()
        shards = gateway_j.get('shards', 1)
        sessions_remaining = gateway_j.get('session_start_limit', {"remaining": -1}).get('remaining', -1)
        sessions_total = gateway_j.get('session_start_limit').get('total', -1)
        reset_after = gateway_j.get('session_start_limit').get('reset_after', 1000)
        print(f'{OKBLUE}Discord recommends starting your bot with {shards} shards! '
              f'You can still start {sessions_remaining}/{sessions_total} sessions!')
        reset = int(time()) + int(reset_after / 1000)
        clean = datetime.fromtimestamp(reset)
        print(f'This limit will reset on {clean.day}-{clean.month}-{clean.year} {clean.hour}:{clean.minute}{ENDC}')
        spc = floor(shards / cluster_count)
        cluster_1 = spc + shards % cluster_count
        names = config.get('cluster_names', [])
        for i in range(0, cluster_count):
            cluster_name = names[i]
            print(f'{OKGREEN}Starting Cluster {cluster_name} ({i}){ENDC}')
            chdir(f'{getcwd()}')
            if i == 0:
                self.start_cluster(path, cluster_1, i, shards, cluster_count, cluster_name)
            else:
                self.start_cluster(path, ceil(spc), i, shards, cluster_count, cluster_name)

    def start_cluster(self, path, shards, cluster, total_shards, cluster_count, cluster_name):
        t = multiprocessing.Process(target=self.run_cluster, args=(path, shards, cluster, total_shards, cluster_count, cluster_name))
        threads.append(t)
        t.start()

    def run_broker(self):
        t = multiprocessing.Process(target=self.run_broker)
        threads.append(t)
        t.start()

    @staticmethod
    def run_cluster(path, shards, cluster, total_shards, cluster_count, cluster_name):
        pc = subprocess.Popen(['python3.6', f'{path}/main.py', str(shards), str(cluster), str(total_shards),
                               str(cluster_count), str(cluster_name)],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        while 1:
            print(pc.stdout.readline().decode().replace('\n', ''))


if __name__ == '__main__':
    App()
