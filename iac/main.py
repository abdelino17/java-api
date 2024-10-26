#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack
from infra.network_stack import NetworkStack
from infra.loab_balancer_stack import LoadBalancerStack
from apps.service_stack import ServiceStack

APPLICATION_NAME = "datadog-apm-demo-service-nodejs"
ENV = "dev"
AWS_REGION = "us-east-1"


class JavaStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # define resources here


app = App()
JavaStack(app, "iac")

NetworkStack(
    app, "network", {"region": AWS_REGION, "application_name": APPLICATION_NAME}
)

LoadBalancerStack(
    app, "load_balancer", {"region": AWS_REGION, "application_name": APPLICATION_NAME}
)

ServiceStack(
    app, "service", {"region": AWS_REGION, "application_name": APPLICATION_NAME}
)

app.synth()
