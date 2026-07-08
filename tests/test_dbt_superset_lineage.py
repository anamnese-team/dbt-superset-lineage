from dbt_superset_lineage import __version__
from dbt_superset_lineage.push_descriptions import extract_certification_from_table, load_manifest_from_s3


def test_version():
    assert __version__ == '0.4.0'


def test_extract_certification_with_nested_meta_and_freshness():
    table = {
        "meta": {
            "certification": {
                "certified_by": "Data Platform",
                "details": "Source of truth for revenue metrics"
            },
            "freshness": "15m"
        }
    }

    certification = extract_certification_from_table(table)

    assert certification["certified_by"] == "Data Platform"
    assert certification["details"] == "Freshness: 15m | Source of truth for revenue metrics"


def test_load_manifest_from_s3_uses_endpoint_url(monkeypatch):
    class Body:
        def read(self):
            return b'{"metadata": {"project_name": "jaffle_shop"}}'

    class S3Client:
        def get_object(self, Bucket, Key):
            assert Bucket == "anamnese-datalake"
            assert Key == "target/manifest.json"
            return {"Body": Body()}

    boto3_client_calls = []

    def boto3_client(service_name, **kwargs):
        boto3_client_calls.append((service_name, kwargs))
        return S3Client()

    monkeypatch.setattr("dbt_superset_lineage.push_descriptions.boto3.client", boto3_client)

    manifest = load_manifest_from_s3(
        "s3://anamnese-datalake/target/manifest.json",
        aws_access_key_id="access-key",
        aws_secret_access_key="secret-key",
        aws_region="gra",
        aws_endpoint_url="https://s3.gra.io.cloud.ovh.net",
    )

    assert manifest["metadata"]["project_name"] == "jaffle_shop"
    assert boto3_client_calls == [
        (
            "s3",
            {
                "region_name": "gra",
                "endpoint_url": "https://s3.gra.io.cloud.ovh.net",
                "aws_access_key_id": "access-key",
                "aws_secret_access_key": "secret-key",
            },
        )
    ]


def test_load_manifest_from_s3_uses_endpoint_url_from_env(monkeypatch):
    class Body:
        def read(self):
            return b'{"metadata": {"project_name": "jaffle_shop"}}'

    class S3Client:
        def get_object(self, Bucket, Key):
            return {"Body": Body()}

    boto3_client_calls = []

    def boto3_client(service_name, **kwargs):
        boto3_client_calls.append((service_name, kwargs))
        return S3Client()

    monkeypatch.setattr("dbt_superset_lineage.push_descriptions.boto3.client", boto3_client)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "gra")
    monkeypatch.setenv("AWS_ENDPOINT_URL", "https://s3.gra.io.cloud.ovh.net")

    load_manifest_from_s3("s3://anamnese-datalake/target/manifest.json", aws_region=None)

    assert boto3_client_calls == [
        (
            "s3",
            {
                "region_name": "gra",
                "endpoint_url": "https://s3.gra.io.cloud.ovh.net",
            },
        )
    ]
