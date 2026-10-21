"""A OCI Python Pulumi program"""

import pulumi
import pulumi_oci as oci
from pulumi import Output

tags = {
    "project": "novachok.pp.ua"
}

homeCompartment = oci.identity.Compartment(
    "novachok.pp.ua-compartment", 
    name="novachok.pp.ua-compartemnt", 
    description="Compartment for novachok.pp.ua project",
    enable_delete=True,
    freeform_tags=tags
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
