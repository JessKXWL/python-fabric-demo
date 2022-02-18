import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test.integration.utils import BaseInit
import logging
import docker
import time
from hfc.util.policies import s2d

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CC_PATH = 'github.com/privacy_cc'
CC_NAME = 'privacy_cc'
CC_VERSION = '1.0'
CC_UPGRADED_VERSION = '1.1'
TOTAL_BLOCKS = 6


class E2eSDK(BaseInit):

    def setUp(self):
        super(E2eSDK, self).setUp()

    def tearDown(self):
        super(E2eSDK, self).tearDown()

    async def channel_create(self):
        """
        Create an channel for further testing.

        :return:
        """
        logger.info(f"E2E: Channel creation start: name={self.channel_name}")

        # By default, self.user is the admin of org1
        response = await self.client.channel_create(
            'orderer.example.com',
            self.channel_name,
            self.user,
            config_yaml=self.config_yaml,
            channel_profile=self.channel_profile)
        assert response

        logger.info(f"E2E: Channel creation done: name={self.channel_name}")

    async def channel_join(self):
        """
        Join peers of two orgs into an existing channels

        :return:
        """

        logger.info(f"E2E: Channel join start: name={self.channel_name}")

        # channel must already exist when to join
        channel = self.client.get_channel(self.channel_name)
        assert channel is not None

        orgs = ["org1.example.com", "org2.example.com"]
        for org in orgs:
            org_admin = self.client.get_user(org, 'Admin')
            response = await self.client.channel_join(
                requestor=org_admin,
                channel_name=self.channel_name,
                peers=['peer0.' + org, 'peer1.' + org],
                orderer='orderer.example.com'
            )
            assert response
            # Verify the ledger exists now in the peer node
            dc = docker.from_env()
            for peer in ['peer0', 'peer1']:
                peer0_container = dc.containers.get(peer + '.' + org)
                code, output = peer0_container.exec_run(
                    'test -f '
                    '/var/hyperledger/production/ledgersData/chains/'
                    f'chains/{self.channel_name}'
                    '/blockfile_000000')
                assert (code, 0, "Local ledger not exists")

        logger.info(f"E2E: Channel join done: name={self.channel_name}")

    async def chaincode_install(self, cc_version=CC_VERSION):
        """
        Test installing an example chaincode to peer
        """
        logger.info("E2E: Chaincode install start")
        cc = f'/var/hyperledger/production/chaincodes/{CC_NAME}.{cc_version}'

        # uncomment for testing with packaged_cc

        # create packaged chaincode before for having same id
        # code_package = package_chaincode(CC_PATH, CC_TYPE_GOLANG)

        orgs = ["org1.example.com", "org2.example.com"]
        for org in orgs:

            # simulate possible different chaincode archive based on timestamp
            time.sleep(2)

            org_admin = self.client.get_user(org, "Admin")
            responses = await self.client.chaincode_install(
                requestor=org_admin,
                peers=['peer0.' + org, 'peer1.' + org],
                cc_path=CC_PATH,
                cc_name=CC_NAME,
                cc_version=cc_version,
                # packaged_cc=code_package
            )
            # assert responses
            print("安装链码的输出", responses)
            # Verify the cc pack exists now in the peer node
            dc = docker.from_env()
            for peer in ['peer0', 'peer1']:
                peer_container = dc.containers.get(peer + '.' + org)
                code, output = peer_container.exec_run(f'test -f {cc}')
                assert (code, 0, "chaincodes pack not exists")

        logger.info("E2E: chaincode install done")

    async def chaincode_instantiate(self):
        """
        Test instantiating an example chaincode to peer
        """
        logger.info("E2E: Chaincode instantiation start")

        org = "org1.example.com"
        args = ['init']

        # policy = s2d().parse("OR('Org1MSP.member', 'Org1MSP.admin')")
        policy = s2d().parse("OR('Org1MSP.member')")

        org_admin = self.client.get_user(org, "Admin")
        response = await self.client.chaincode_instantiate(
            requestor=org_admin,
            channel_name=self.channel_name,
            peers=['peer0.' + org],
            args=args,
            cc_name=CC_NAME,
            cc_version=CC_VERSION,
            cc_endorsement_policy=policy,
            wait_for_event=True
        )
        logger.info(
            "E2E: Chaincode instantiation response {}".format(response))
        policy = {
            'version': 0,
            'rule': {'n_out_of': {
                'n': 1,
                'rules': [
                    {'signed_by': 0},
                    # {'signed_by': 1}
                ]}
            },
            'identities': [
                {
                    'principal_classification': 'ROLE',
                    'principal': {
                        'msp_identifier': 'Org1MSP',
                        'role': 'MEMBER'
                    }
                },
                # {
                #     'principal_classification': 'ROLE',
                #     'principal': {
                #         'msp_identifier': 'Org1MSP',
                #         'role': 'ADMIN'
                #     }
                # },
            ]
        }
        assert response['name'] == CC_NAME
        assert response['version'] == CC_VERSION
        assert response['policy'] == policy
        logger.info("E2E: chaincode instantiation done")

    async def chaincode_upgrade(self, args, cc_version):
        """
        Test upgrading an example chaincode
        """
        logger.info("E2E: Chaincode upgrade start")

        org = "org1.example.com"
        # args = ['a', '200', 'b', '300']

        # policy = s2d().parse("OR('Org1MSP.member', 'Org1MSP.admin')")
        policy = s2d().parse("OR('Org1MSP.member')")

        org_admin = self.client.get_user(org, "Admin")
        response = await self.client.chaincode_upgrade(
            requestor=org_admin,
            channel_name=self.channel_name,
            peers=['peer0.' + org],
            args=args,
            cc_name=CC_NAME,
            cc_version=cc_version,
            cc_endorsement_policy=policy,
            wait_for_event=True
        )
        logger.info(
            "E2E: Chaincode instantiation response {}".format(response))
        policy = {
            'version': 0,
            'rule': {'n_out_of': {
                'n': 1,
                'rules': [
                    {'signed_by': 0},
                    # {'signed_by': 1}
                ]}
            },
            'identities': [
                {
                    'principal_classification': 'ROLE',
                    'principal': {
                        'msp_identifier': 'Org1MSP',
                        'role': 'MEMBER'
                    }
                },
                # {
                #     'principal_classification': 'ROLE',
                #     'principal': {
                #         'msp_identifier': 'Org1MSP',
                #         'role': 'ADMIN'
                #     }
                # },
            ]
        }
        assert response['name'] == CC_NAME
        assert response['version'] == CC_VERSION
        assert response['policy'] == policy
        logger.info("E2E: chaincode instantiation done")

    async def chaincode_invoke(self, args, orgs=None):
        """
        Test invoking an example chaincode to peer

        :return:
        """
        logger.info("E2E: Chaincode invoke start")
        if orgs is None:
            orgs = ["org1.example.com"]

        if args[0] == "add":
            cc_pattern = "^added*"
        elif args[0] == "update":
            cc_pattern = "^updated*"
        elif args[0] == "delete":
            cc_pattern = "^deleted*"
        else:
            logger.info("E2E: Chaincode invoke did not find func: ", args[0])
            return False
        for org in orgs:
            org_admin = self.client.get_user(org, "Admin")

            response = await self.client.chaincode_invoke(
                fcn=args[0],
                requestor=org_admin,
                channel_name=self.channel_name,
                peers=['peer1.' + org],
                args=args[1:],
                cc_name=CC_NAME,
                wait_for_event=True,
                wait_for_event_timeout=240,
                cc_pattern=cc_pattern  # for chaincode event
            )
            logger.info("E2E: chaincode invoke done")
            print("invoke的返回数据", response)
            return response

    async def chaincode_query(self, args, orgs=None):
        """
        Test invoking an example chaincode to peer

        :return:
        """
        logger.info("E2E: Chaincode query start")

        if orgs is None:
            orgs = ["org1.example.com"]
        for org in orgs:
            org_admin = self.client.get_user(org, "Admin")
            response = await self.client.chaincode_invoke(
                fcn=args[0],
                requestor=org_admin,
                channel_name=self.channel_name,
                peers=['peer0.' + org],
                args=args[1:],
                cc_name=CC_NAME
            )
        logger.info("E2E: chaincode query done")
        return response
