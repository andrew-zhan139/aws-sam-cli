import os
import time
import boto3
import re
from unittest import skipIf
from tests.integration.deploy.deploy_integ_base import DeployIntegBase
from tests.integration.list.resources.resources_integ_base import ResourcesIntegBase
from samcli.commands.list.resources.cli import HELP_TEXT
from tests.testing_utils import run_command
from tests.testing_utils import RUNNING_ON_CI, RUNNING_TEST_FOR_MASTER_ON_CI, RUN_BY_CANARY
from tests.testing_utils import run_command, run_command_with_input, method_to_stack_name

SKIP_STACK_OUTPUTS_TESTS = RUNNING_ON_CI and RUNNING_TEST_FOR_MASTER_ON_CI and not RUN_BY_CANARY
CFN_SLEEP = 3
CFN_PYTHON_VERSION_SUFFIX = os.environ.get("PYTHON_VERSION", "0.0.0").replace(".", "-")


@skipIf(SKIP_STACK_OUTPUTS_TESTS, "Skip stack-outputs tests in CI/CD only")
class TestResources(ResourcesIntegBase):
    @classmethod
    def setUpClass(cls):
        DeployIntegBase.setUpClass()
        ResourcesIntegBase.setUpClass()

    def setUp(self):
        self.cf_client = boto3.client("cloudformation")
        time.sleep(CFN_SLEEP)
        super().setUp()

    def test_resources_help_message(self):
        cmdlist = self.get_resources_command_list(help=True)
        command_result = run_command(cmdlist)
        from_command = "".join(command_result.stdout.decode().split())
        from_help = "".join(HELP_TEXT.split())
        self.assertIn(from_help, from_command, "Resources help text should have been printed")

    def test_successful_transform(self):
        template_path = self.list_test_data_path.joinpath("test_stack_creation_template.yaml")
        region = boto3.Session().region_name
        cmdlist = self.get_resources_command_list(
            stack_name=None, region=region, output="json", template_file=template_path
        )
        command_result = run_command(cmdlist, cwd=self.working_dir)
        self.assertIn(
            """{
  "LogicalResourceId": "HelloWorldFunction",
  "PhysicalResourceId": "-"
}""",
            command_result.stdout.decode(),
        )
        self.assertIn(
            """{
  "LogicalResourceId": "HelloWorldFunctionRole",
  "PhysicalResourceId": "-"
}""",
            command_result.stdout.decode(),
        )
        self.assertIn(
            """{
  "LogicalResourceId": "HelloWorldFunctionHelloWorldPermissionProd",
  "PhysicalResourceId": "-"
}""",
            command_result.stdout.decode(),
        )
        self.assertIn(
            """{
  "LogicalResourceId": "ServerlessRestApi",
  "PhysicalResourceId": "-"
}""",
            command_result.stdout.decode(),
        )
        self.assertIn(
            """{
  "LogicalResourceId": "ServerlessRestApiProdStage",
  "PhysicalResourceId": "-"
}""",
            command_result.stdout.decode(),
        )
        self.assertTrue(
            re.search(
                """{
  "LogicalResourceId": "ServerlessRestApiDeployment.*",
  "PhysicalResourceId": "-"
}""",
                command_result.stdout.decode(),
            )
        )

    def test_invalid_template_file(self):
        template_path = self.list_test_data_path.joinpath("test_resources_invalid_sam_template.yaml")
        region = boto3.Session().region_name
        cmdlist = self.get_resources_command_list(
            stack_name=None, region=region, output="json", template_file=template_path
        )
        command_result = run_command(cmdlist, cwd=self.working_dir)
        self.assertIn("Template provided was invalid SAM Template.", command_result.stdout.decode())