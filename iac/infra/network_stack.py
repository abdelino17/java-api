from constructs import Construct
from cdktf import S3Backend, TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.vpc import Vpc
from cdktf_cdktf_provider_aws.subnet import Subnet
from cdktf_cdktf_provider_aws.eip import Eip
from cdktf_cdktf_provider_aws.nat_gateway import NatGateway
from cdktf_cdktf_provider_aws.route import Route
from cdktf_cdktf_provider_aws.route_table import RouteTable
from cdktf_cdktf_provider_aws.route_table_association import RouteTableAssociation
from cdktf_cdktf_provider_aws.internet_gateway import InternetGateway


class NetworkStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str, params: dict):
        super().__init__(scope, ns)

        self.region = params["region"]

        # Configure the AWS provider to use the us-east-1 region
        AwsProvider(self, "AWS", region=self.region)

        S3Backend(
            self,
            bucket="blog.abdelfare.me",
            key="cdktf-samples/fargate-demo/network.tfstate",
            region=self.region,
        )

        # vpc
        vpc_demo = Vpc(self, "vpc-demo", cidr_block="192.168.0.0/16")

        # public
        public_subnet1 = Subnet(
            self,
            "public-subnet-1",
            vpc_id=vpc_demo.id,
            availability_zone=f"{self.region}a",
            cidr_block="192.168.1.0/24",
        )

        public_subnet2 = Subnet(
            self,
            "public-subnet-2",
            vpc_id=vpc_demo.id,
            availability_zone=f"{self.region}b",
            cidr_block="192.168.2.0/24",
        )

        igw = InternetGateway(self, "igw", vpc_id=vpc_demo.id)

        public_rt = Route(
            self,
            "public-rt",
            route_table_id=vpc_demo.main_route_table_id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )

        # private
        private_subnet = Subnet(
            self,
            "private-subnet",
            vpc_id=vpc_demo.id,
            availability_zone=f"{self.region}a",
            cidr_block="192.168.10.0/24",
        )

        private_eip = Eip(self, "nat-eip", vpc=True, depends_on=[igw])

        private_nat = NatGateway(
            self,
            "private-nat",
            subnet_id=public_subnet1.id,
            allocation_id=private_eip.id,
        )

        private_rt = RouteTable(self, "private-rt", vpc_id=vpc_demo.id)

        Route(
            self,
            "private-rt-default-route",
            route_table_id=private_rt.id,
            destination_cidr_block="0.0.0.0/0",
            nat_gateway_id=private_nat.id,
        )

        RouteTableAssociation(
            self,
            "private-rt-association",
            subnet_id=private_subnet.id,
            route_table_id=private_rt.id,
        )

        TerraformOutput(self, "vpc_id", value=vpc_demo.id)
        TerraformOutput(
            self, "public_subnets", value=[public_subnet1.id, public_subnet2.id]
        )
        TerraformOutput(self, "private_subnets", value=[private_subnet.id])
