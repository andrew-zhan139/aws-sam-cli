import os
import time
import boto3
import re
from unittest import skipIf
from tests.integration.deploy.deploy_integ_base import DeployIntegBase
from tests.integration.list.testable_resources.testable_resources_integ_base import TestableResourcesIntegBase
from samcli.commands.list.testable_resources.cli import HELP_TEXT
from tests.testing_utils import run_command
from tests.testing_utils import RUNNING_ON_CI, RUNNING_TEST_FOR_MASTER_ON_CI, RUN_BY_CANARY
from tests.testing_utils import run_command, run_command_with_input, method_to_stack_name

SKIP_TESTABLE_RESOURCES_TESTS = RUNNING_ON_CI and RUNNING_TEST_FOR_MASTER_ON_CI and not RUN_BY_CANARY
CFN_SLEEP = 3
CFN_PYTHON_VERSION_SUFFIX = os.environ.get("PYTHON_VERSION", "0.0.0").replace(".", "-")


@skipIf(SKIP_TESTABLE_RESOURCES_TESTS, "Skip testable resources tests in CI/CD only")
class TestTestableResources(DeployIntegBase, TestableResourcesIntegBase):
    @classmethod
    def setUpClass(cls):
        DeployIntegBase.setUpClass()
        TestableResourcesIntegBase.setUpClass()

    def setUp(self):
        self.cf_client = boto3.client("cloudformation")
        time.sleep(CFN_SLEEP)
        super().setUp()

    def test_testable_resources_help_message(self):
        cmdlist = self.get_testable_resources_command_list(help=True)
        command_result = run_command(cmdlist)
        from_command = "".join(command_result.stdout.decode().split())
        from_help = "".join(HELP_TEXT.split())
        self.assertIn(from_help, from_command, "Testable-resources help text should have been printed")

    def test_no_stack_name(self):
        template_path = self.list_test_data_path.joinpath("test_testable_resources_template.yaml")
        region = boto3.Session().region_name
        cmdlist = self.get_testable_resources_command_list(
            stack_name=None, region=region, output="json", template_file=template_path
        )
        command_result = run_command(cmdlist, cwd=self.working_dir)
        expected_output = [
            """{
    "LogicalResourceId": "HelloWorldFunction",
    "PhysicalResourceId": "-",
    "CloudEndpointOrFunctionURL": "-",
    "Methods": "-"
  }""",
            """{
    "LogicalResourceId": "TestAPI",
    "PhysicalResourceId": "-",
    "CloudEndpointOrFunctionURL": "-",
    "Methods": []
  }""",
            """{
    "LogicalResourceId": "ServerlessRestApi",
    "PhysicalResourceId": "-",
    "CloudEndpointOrFunctionURL": "-",
    "Methods": [
      "/hello2['get']",
      "/hello['get']"
    ]
  }""",
        ]
        for expression in expected_output:
            self.assertIn(expression, command_result.stdout.decode())

    def test_has_stack_name(self):
        template_path = self.list_test_data_path.joinpath("test_testable_resources_template.yaml")
        stack_name = method_to_stack_name(self.id())
        config_file_name = stack_name + ".toml"
        region = boto3.Session().region_name
        deploy_command_list = self.get_deploy_command_list(
            template_file=template_path,
            guided=True,
            config_file=config_file_name,
            region=region,
            confirm_changeset=True,
            disable_rollback=True,
        )
        deploy_process_execute = run_command_with_input(
            deploy_command_list, "{}\n{}\nY\nY\nY\nY\nY\nY\n\n\nY\n".format(stack_name, region).encode()
        )
        cmdlist = self.get_testable_resources_command_list(
            stack_name=stack_name, region=region, output="json", template_file=template_path
        )
        command_result = run_command(cmdlist, cwd=self.working_dir)
        expected_output = [
            """{
    "LogicalResourceId": "HelloWorldFunction",
    "PhysicalResourceId": "test-has-stack-name.*",
    "CloudEndpointOrFunctionURL": "https://.*.lambda-url..*.on.aws/",
    "Methods": "-"
  }""",
            """  {
    "LogicalResourceId": "ServerlessRestApi",
    "PhysicalResourceId": ".*",
    "CloudEndpointOrFunctionURL": .*
      "https://.*.execute-api..*.amazonaws.com/Prod",
      "https://.*.execute-api..*.amazonaws.com/Stage"
    .*,
    "Methods": .*
      "/hello2.'get'.",
      "/hello.'get'."
    .
  }""",
            """  {
    "LogicalResourceId": "TestAPI",
    "PhysicalResourceId": ".*",
    "CloudEndpointOrFunctionURL": .
      "https://.*.execute-api..*.amazonaws.com/Test2"
    .,
    "Methods": ..
  }""",
        ]
        for expression in expected_output:
            self.assertTrue(re.search(expression, command_result.stdout.decode()))

    def test_stack_does_not_exist(self):
        template_path = self.list_test_data_path.joinpath("test_testable_resources_template.yaml")
        stack_name = method_to_stack_name(self.id())
        config_file_name = stack_name + ".toml"
        region = boto3.Session().region_name
        cmdlist = self.get_testable_resources_command_list(
            stack_name=stack_name, region=region, output="json", template_file=template_path
        )
        command_result = run_command(cmdlist, cwd=self.working_dir)
        expected_output = (
            f"Error: The input stack {stack_name} does" f" not exist on Cloudformation in the region {region}"
        )
        self.assertIn(
            expected_output, command_result.stderr.decode(), "Should have raised error that outputs do not exist"
        )
