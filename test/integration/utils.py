import uuid
import os
import time
import subprocess

import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hfc.fabric.client import Client
from hfc.fabric.user import create_user
from test.integration.config import E2E_CONFIG

class BaseInit(object):
    """
    创建接口的Base类
    """
    def setUp(self):
        self.gopath_bak = os.environ.get('GOPATH', '')
        gopath = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                               "../fixtures/chaincode"))
        os.environ['GOPATH'] = os.path.abspath(gopath)
        self.channel_tx = \
            E2E_CONFIG['test-network']['channel-artifacts']['channel.tx']
        self.compose_file_path = \
            E2E_CONFIG['test-network']['docker']['compose_file_tls']

        self.config_yaml = \
            E2E_CONFIG['test-network']['channel-artifacts']['config_yaml']
        self.channel_profile = \
            E2E_CONFIG['test-network']['channel-artifacts']['channel_profile']
        self.client = Client('test/fixtures/network.json')
        self.channel_name = "businesschannel"  # default application channel
        self.user = self.client.get_user('org1.example.com', 'Admin')

        # Boot up the testing network
        self.shutdown_test_env()
        self.start_test_env()
        time.sleep(1)

        time.sleep(1)

    def tearDown(self):
        time.sleep(1)
        self.shutdown_test_env()

    def check_logs(self):
        cli_call(["docker-compose", "-f", self.compose_file_path, "logs",
                  "--tail=200"])

    def start_test_env(self):
        print("set-up")
        cli_call(["docker-compose", "-f", self.compose_file_path, "up", "-d"])

    def shutdown_test_env(self):
        print("tear down")
        self.check_logs()
        cli_call(["docker-compose", "-f", self.compose_file_path, "down"])

def cli_call(arg_list, expect_success=True, env=os.environ.copy()):
    """Executes a CLI command in a subprocess and return the results.

    Args:
        arg_list: a list command arguments
        expect_success: use False to return even if an error occurred
                        when executing the command
        env:

    Returns: (string, string, int) output message, error message, return code

    """
    p = subprocess.Popen(arg_list, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env)
    output, error = p.communicate()
    if p.returncode != 0:
        if output:
            print("Output:\n" + str(output))
        if error:
            print("Error Message:\n" + str(error))
        if expect_success:
            raise subprocess.CalledProcessError(
                p.returncode, arg_list, output)
    return output, error, p.returncode