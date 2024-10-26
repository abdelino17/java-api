from importlib.resources import path
from constructs import Construct
import json
from cdktf import S3Backend, TerraformStack, TerraformOutput, DataTerraformRemoteStateS3
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.ecs_service import (
    EcsService,
    EcsServiceConfig,
    EcsServiceLoadBalancer,
    EcsServiceNetworkConfiguration,
)
from cdktf_cdktf_provider_aws.ecs_task_definition import (
    EcsTaskDefinition,
    EcsTaskDefinitionRuntimePlatform,
)
from cdktf_cdktf_provider_aws.lb_listener_rule import (
    LbListenerRule,
    LbListenerRuleAction,
    LbListenerRuleCondition,
    LbListenerRuleConditionPathPattern,
)
from cdktf_cdktf_provider_aws.lb_target_group import (
    LbTargetGroup,
    LbTargetGroupHealthCheck,
)
from cdktf_cdktf_provider_aws.security_group import (
    SecurityGroup,
    SecurityGroupIngress,
    SecurityGroupEgress,
)


class ServiceStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str, params: dict):
        super().__init__(scope, ns)

        self.region = params["region"]

        # Configure the AWS provider to use the us-east-1 region
        AwsProvider(self, "AWS", region=self.region)

        S3Backend(
            self,
            bucket="blog.abdelfare.me",
            key="cdktf-samples/fargate-demo/service.tfstate",
            region=self.region,
        )

        networkState = DataTerraformRemoteStateS3(
            self,
            "network",
            bucket="blog.abdelfare.me",
            key="cdktf-samples/fargate-demo/network.tfstate",
            region=self.region,
        )

        lbState = DataTerraformRemoteStateS3(
            self,
            "load_balancer",
            bucket="blog.abdelfare.me",
            key="cdktf-samples/fargate-demo/load_balancer.tfstate",
            region=self.region,
        )

        svc_sg = SecurityGroup(
            self,
            "svc-sg",
            vpc_id=networkState.get_string("vpc_id"),
            ingress=[
                SecurityGroupIngress(
                    protocol="tcp",
                    from_port=8080,
                    to_port=8080,
                    security_groups=[lbState.get_string("alb_sg")],
                )
            ],
            egress=[
                SecurityGroupEgress(
                    protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"]
                )
            ],
        )

        svc_tg = LbTargetGroup(
            self,
            "svc-target-group",
            name="svc-tg",
            port=8080,
            protocol="HTTP",
            vpc_id=networkState.get_string("vpc_id"),
            target_type="ip",
            health_check=LbTargetGroupHealthCheck(path="/ping", matcher="200"),
        )

        LbListenerRule(
            self,
            "alb-rule",
            listener_arn=lbState.get_string("alb_listener"),
            action=[LbListenerRuleAction(type="forward", target_group_arn=svc_tg.arn)],
            condition=[
                LbListenerRuleCondition(
                    path_pattern=LbListenerRuleConditionPathPattern(values=["/*"])
                )
            ],
        )

        task = EcsTaskDefinition(
            self,
            "svc-task",
            family="service",
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            cpu="256",
            memory="512",
            runtime_platform=EcsTaskDefinitionRuntimePlatform(
                operating_system_family="LINUX", cpu_architecture="ARM64"
            ),
            container_definitions=json.dumps(
                [
                    {
                        "name": "svc",
                        "image": "abdelino/java-api:v1.2.0",
                        "networkMode": "awsvpc",
                        "portMappings": [{"containerPort": 8080, "hostPort": 8080}],
                    }
                ]
            ),
        )

        EcsService(
            self,
            "service",
            name="service",
            cluster=lbState.get_string("cluster_id"),
            task_definition=task.arn,
            desired_count=1,
            launch_type="FARGATE",
            network_configuration=EcsServiceNetworkConfiguration(
                subnets=networkState.get_list("private_subnets"),
                security_groups=[svc_sg.id],
            ),
            load_balancer=[
                EcsServiceLoadBalancer(
                    target_group_arn=svc_tg.id,
                    container_name="svc",
                    container_port=8080,
                )
            ],
        )
