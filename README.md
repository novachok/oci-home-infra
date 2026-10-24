To authorithe Pulumi to work with OCI bucket as a state storage:

```
export AWS_SECRET_ACCESS_KEY="...."
export AWS_ACCESS_KEY_ID="...."

pulumi login 's3://infra-state?endpoint=<NAMESPACE>.compat.objectstorage.<REGION>.oraclecloud.com&region=<REGION>&s3ForcePathStyle=true&disableSSL=false'


## Get available shapes
```
oci compute shape list \
    --compartment-id "<Compartement ID>" \
    --all
```

## Get available images
```
oci compute image list \
  --compartment-id "<Compartement ID>" \
  --operating-system "Canonical Ubuntu" \
  --shape VM.Standard.A1.Flex
```