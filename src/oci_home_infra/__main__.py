"""A OCI Python Pulumi program"""

import pulumi
import pulumi_oci as oci
from pulumi import Output

AVAILABILITY_DOMAIN = "oIkP:EU-FRANKFURT-1-AD-2"

tags = {
    "project": "nppua"
}

compartment = oci.identity.Compartment(
    "nppua-compartment", 
    name="nppua-compartemnt", 
    description="Compartment for Home project",
    enable_delete=True,
    freeform_tags=tags
)

namespace = Output.all(compartment.id).apply(
    lambda args: oci.objectstorage.get_namespace(compartment_id=args[0])
)

vcn = oci.core.Vcn(
    "nppua-vcn",
    compartment_id=compartment.id,
    cidr_blocks=["10.0.0.0/24"],
    display_name="Home VCN",
    freeform_tags=tags
)

gateway = oci.core.InternetGateway(
    "nppua-internet-gateway",
    compartment_id=compartment.id,
    vcn_id=vcn.id,
    display_name="Home VCN Internet Gateway",
    enabled=True,
    freeform_tags=tags
)

route_table = oci.core.RouteTable(
    "nppua-route-table",
    compartment_id=compartment.id,
    vcn_id=vcn.id,
    display_name="Home VCN Router Table",
    route_rules=[{
        "network_entity_id": gateway.id,
        "description": "Internet Access via IGW",
        "destination": "0.0.0.0/0",
        "destination_type": "CIDR_BLOCK"
    }],
    freeform_tags=tags
)

pub_subnet = oci.core.Subnet(
    "nppua-public-subnet",
    compartment_id=compartment.id,
    vcn_id=vcn.id,
    route_table_id=route_table.id,
    display_name="Home VCN Public subnet",
    cidr_block="10.0.0.0/24",
    freeform_tags=tags
)

security_rules = oci.core.SecurityList(
    "nppua-security-list",
    compartment_id=compartment.id,
    vcn_id=vcn.id,
    display_name="Dev Intance Security Rules",
    egress_security_rules=[{
        "destination": "0.0.0.0/0",
        "destination_type": "CIDR_BLOCK",
        "protocol": "all",
        "stateless": False
    }],
    ingress_security_rules=[{
        "description": "SSH (TCP 22)",
        "source": "0.0.0.0/0",
        "source_type": "CIDR_BLOCK",
        "protocol": "6",
        "stateless": False,
        "tcp_options": {
            "min": 22,
            "max": 22
        }
    }, {
        "description": "HTTP (TCP 80)",
        "source": "0.0.0.0/0",
        "source_type": "CIDR_BLOCK",
        "protocol": "6",
        "stateless": False,
        "tcp_options": {
            "min": 80,
            "max": 80
        }
    }, {
        "description": "HTTPS (TCP 443)",
        "source": "0.0.0.0/0",
        "source_type": "CIDR_BLOCK",
        "protocol": "6",
        "stateless": False,
        "tcp_options": {
            "min": 443,
            "max": 443
        }
    }, {
        "description": "HTTP development ports (TCP 8000 ... 8100)",
        "source": "0.0.0.0/0",
        "source_type": "CIDR_BLOCK",
        "protocol": "6",
        "stateless": False,
        "tcp_options": {
            "min": 8000,
            "max": 8100
        }
    }, {
        "description": "ICMP: Destination Unreachable (Type 3, Code 4)",
        "source": "0.0.0.0/0",
        "source_type": "CIDR_BLOCK",
        "protocol": "1",
        "stateless": False,
        "icmp_options": {
            "type": 3,
            "code": 4
        }
    }, {
        "description": "ICMP: Destination Unreachable (Type 3, any code)",
        "source": "10.0.0.0/24",
        "source_type": "CIDR_BLOCK",
        "protocol": "1",
        "stateless": False,
        "icmp_options": {
            "type": 3
        }
    }],
    freeform_tags=tags
)

# VM.Standard.A1.Flex
# Canonical-Ubuntu-26.04-aarch64-2026.08.17-0
# ID: ocid1.image.oc1.eu-frankfurt-1.aaaaaaaa4h6cquo34kh2emfor6rcdsns2j7ypontupg44qmkn5xdxcvox3mq
#
# Availability domain: oIkP:EU-FRANKFURT-1-AD-2
# ID: ocid1.availabilitydomain.oc1..aaaaaaaaiifj24st3w4j7cowuo3pmqcuqwjapjv435vtjmgh5j7q3flguwna

instance = oci.core.Instance(
    "nppua-instance",
    compartment_id=compartment.id,
    availability_domain=AVAILABILITY_DOMAIN,
    display_name="Home Dev Instance",
    shape="VM.Standard.A1.Flex",
    shape_config={
        "ocpus": 2,
        "memory_in_gbs": 12
    },
    create_vnic_details={
        "subnet_id": pub_subnet.id,
        "display_name": "VNIC0",
        "assign_public_ip": False
    },
    source_details={
        "source_type": "image",
        "source_id": "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaa4h6cquo34kh2emfor6rcdsns2j7ypontupg44qmkn5xdxcvox3mq",
        "boot_volume_size_in_gbs": 50
    },
    metadata={
        "ssh_authorized_keys": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKs4bY5X333WXKZkZ7jmeA4+kqVf2Hg0AmWnzGpNs+y4",
        "user_data": "I2Nsb3VkLWNvbmZpZwpwYWNrYWdlczoKICAtIGdpdAogIC0gZG9ja2VyLmlvCnJ1bmNtZDoKICAtIGFwdC1nZXQgdXBkYXRlIC15CiAgLSBhcHQtZ2V0IHVwZ3JhZGUgLXkKICAtIHN5c3RlbWN0bCBlbmFibGUgZG9ja2VyCiAgLSBzeXN0ZW1jdGwgc3RhcnQgZG9ja2Vy"
    },
    freeform_tags=tags
)


vnic_attachments = oci.core.get_vnic_attachments(
    compartment_id=compartment.id,
    availability_domain=AVAILABILITY_DOMAIN,
    instance_id=instance.id
)

try:
    vnic_id = vnic_attachments.vnic_attachments[0].vnic_id
except IndexError:
    print(f"VNIC is not available in the Instance ID: [{instance.id}]")
    exit()

private_ips = oci.core.get_private_ips(vnic_id=vnic_id)

try:
    private_ip = private_ips.private_ips[0]
except IndexError:
    print(f"VNIC doesn't have assigend Private IP")


reserved_public_ip = oci.core.PublicIp(
    "nppua-public-ip",
    compartment_id=compartment.id,
    lifetime="RESERVED",
    display_name="IP for novachok.pp.ua domain",
    private_ip_id=private_ip.id,
    freeform_tags=tags
)


myBucket = oci.objectstorage.Bucket(
    "test-bucket", 
    name="test-bucket", 
    namespace=namespace.namespace,
    compartment_id=compartment.id
)
# Export the Instance label of the instance
pulumi.export('bucket name', myBucket.name)
pulumi.export('private ip', private_ip.ip_address)
pulumi.export('public ip', reserved_public_ip.ip_address)