"""A OCI Python Pulumi program"""

import pulumi
import pulumi_oci as oci
from pulumi import Output

homeCompartment = oci.identity.Compartment(
    "homeCompartment", 
    name="home-compartment", 
    description="home-compartment",
    enable_delete=True
)

namespace = Output.all(homeCompartment.id).apply(
    lambda args: oci.objectstorage.get_namespace(compartment_id=args[0])
)

myBucket = oci.objectstorage.Bucket(
    "test-bucket", 
    name="test-bucket", 
    namespace=namespace.namespace,
    compartment_id=homeCompartment.id
)

# Export the Instance label of the instance
pulumi.export('name', myBucket.name)
