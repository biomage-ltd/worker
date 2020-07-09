from config import get_config
import boto3
import datetime
import anndata
import io
from helpers.dynamo import get_item_from_dynamo

config = get_config()


def _download_obj(bucket, key):
    try:
        client = boto3.client("s3")
        result = io.BytesIO()
        client.download_fileobj(Bucket=bucket, Key=key, Fileobj=result)
        result.seek(0)
    except Exception as e:
        print(datetime.datetime.now(), "Could not get file from S3", e)
        raise e
    print(datetime.datetime.now(), "File was loaded.")
    return result


def _load_file(matrix_path):
    print(config.ENVIRONMENT)
    # intercept here if task is to prepare experiment, don't download from s3
    if config.ENVIRONMENT != "development":
        print(datetime.datetime.now(), "Have to download anndata file from s3")
        bucket, key = matrix_path.split("/", 1)
        result = _download_obj(bucket, key)
        adata = anndata.read_h5ad(result)
    else:
        with open("./tests/test.h5ad", "rb") as f:
            adata = anndata.read_h5ad(f)

    print(datetime.datetime.now(), "File was loaded.")

    if "cell_ids" not in adata.obs:
        raise ValueError(
            "You must have `cell_ids` in your anndata file for integer cell IDs."
        )

    return adata


def get_adata(adata, experiment_id):
    print(datetime.datetime.now(), "adata does not exist, I need to download it ...")
    matrix_path = get_item_from_dynamo(experiment_id, "matrixPath")
    adata = _load_file(matrix_path)
    return adata
