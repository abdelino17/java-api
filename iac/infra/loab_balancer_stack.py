from constructs import Construct
from cdktf import S3Backend, TerraformStack, TerraformOutput, DataTerraformRemoteStateS3
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.ecs_cluster import EcsCluster
from cdktf_cdktf_provider_aws.lb import Lb
from cdktf_cdktf_provider_aws.lb_listener import (
    LbListener,
    LbListenerDefaultAction,
    LbListenerDefaultActionFixedResponse,
)
from cdktf_cdktf_provider_aws.security_group import (
    SecurityGroup,
    SecurityGroupIngress,
    SecurityGroupEgress,
)


class LoadBalancerStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str, params: dict):
        super().__init__(scope, ns)

        self.region = params["region"]

        # Configure the AWS provider to use the us-east-1 region
        AwsProvider(self, "AWS", region=self.region)

        S3Backend(
            self,
            bucket="blog.abdelfare.me",
            key="cdktf-samples/fargate-demo/load_balancer.tfstate",
            region=self.region,
        )

        networkState = DataTerraformRemoteStateS3(
            self,
            "network",
            bucket="blog.abdelfare.me",
            key="cdktf-samples/fargate-demo/network.tfstate",
            region=self.region,
        )

        alb_sg = SecurityGroup(
            self,
            "alb-sg",
            vpc_id=networkState.get_string("vpc_id"),
            ingress=[
                SecurityGroupIngress(
                    protocol="tcp", from_port=80, to_port=80, cidr_blocks=["0.0.0.0/0"]
                )
            ],
            egress=[
                SecurityGroupEgress(
                    protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"]
                )
            ],
        )

        alb = Lb(
            self,
            "alb",
            internal=False,
            load_balancer_type="application",
            security_groups=[alb_sg.id],
            subnets=networkState.get_list("public_subnets"),
        )

        alb_listener = LbListener(
            self,
            "alb-listener",
            load_balancer_arn=alb.arn,
            port=80,
            protocol="HTTP",
            default_action=[
                LbListenerDefaultAction(
                    type="fixed-response",
                    fixed_response=LbListenerDefaultActionFixedResponse(
                        content_type="text/plain",
                        status_code="404",
                        message_body="Could not find the resource you are looking for",
                    ),
                )
            ],
        )

        cluster = EcsCluster(self, "cluster", name="java-api")

        TerraformOutput(self, "alb_arn", value=alb.arn)
        TerraformOutput(self, "alb_listener", value=alb_listener.arn)
        TerraformOutput(self, "alb_sg", value=alb_sg.id)
        TerraformOutput(self, "cluster_id", value=cluster.id)
