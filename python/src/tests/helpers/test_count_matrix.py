import os
import shutil
import boto3
from moto import mock_s3
from pathlib import Path
from helpers.count_matrix import CountMatrix
from config import get_config

config = get_config()


class TestCountMatrix:
    def get_count_matrix_instance(self):
        s3 = boto3.client("s3", **config.BOTO_RESOURCE_KWARGS)
        bucket = config.SOURCE_BUCKET
        self.key = f"{config.EXPERIMENT_ID}/python.h5ad"
        self.local_path = os.path.join(config.LOCAL_DIR, config.EXPERIMENT_ID)
        self.adata_path = os.path.join(config.LOCAL_DIR, self.key)

        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={"LocationConstraint": config.AWS_REGION},
        )

        with open(os.path.join(config.LOCAL_DIR, "test", "python.h5ad"), "rb") as f:
            s3.upload_fileobj(Fileobj=f, Bucket=bucket, Key=self.key)

        self.count_matrix = CountMatrix()
        self.count_matrix.s3 = s3

    @mock_s3
    def test_get_objects(self):
        self.get_count_matrix_instance()
        objs = self.count_matrix.get_objects()
        assert objs == {
            "5e959f9c9f4b120771249001/python.h5ad": '"ad429334fb2de1b0eb8077ba7e222941-5"'
        }

    @mock_s3
    def test_download_object_does_not_exist(self):
        self.get_count_matrix_instance()
        self.count_matrix.path_exists = False
        Path(self.local_path).mkdir(parents=True, exist_ok=True)
        is_downloaded = self.count_matrix.download_object(self.key, "567")
        assert is_downloaded

    @mock_s3
    def test_download_object_previously_existing_etag_doesnt_match(self):
        self.get_count_matrix_instance()
        self.count_matrix.path_exists = True
        Path(self.local_path).mkdir(parents=True, exist_ok=True)
        is_downloaded = self.count_matrix.download_object(self.key, "567")
        assert is_downloaded

    @mock_s3
    def test_download_object_previously_existing_etag_does_match(self):
        self.get_count_matrix_instance()
        self.count_matrix.path_exists = True
        Path(self.local_path).mkdir(parents=True, exist_ok=True)
        is_downloaded = self.count_matrix.download_object(
            self.key,
            self.count_matrix.calculate_file_etag(
                os.path.join(config.LOCAL_DIR, "test", "python.h5ad")
            ),
        )
        assert not is_downloaded

    @mock_s3
    def test_sync_no_previous_data(self):
        self.get_count_matrix_instance()
        self.count_matrix.path_exists = True
        shutil.rmtree(self.local_path, ignore_errors=True)

        self.count_matrix.sync()
        assert "AnnData" in type(self.count_matrix.adata).__name__
        assert not self.count_matrix.path_exists
        assert Path(self.local_path).exists()
        assert self.count_matrix.calculate_file_etag(
            self.adata_path
        ) == self.count_matrix.calculate_file_etag(
            os.path.join(config.LOCAL_DIR, "test", "python.h5ad")
        )

    @mock_s3
    def test_sync_previous_data_changed(self):
        self.get_count_matrix_instance()
        self.count_matrix.path_exists = True

        shutil.rmtree(self.local_path, ignore_errors=True)
        Path(self.local_path).mkdir(parents=True, exist_ok=True)
        Path(self.adata_path).touch(exist_ok=True)

        assert self.count_matrix.calculate_file_etag(
            self.adata_path
        ) != self.count_matrix.calculate_file_etag(
            os.path.join(config.LOCAL_DIR, "test", "python.h5ad")
        )

        self.count_matrix.sync()
        assert "AnnData" in type(self.count_matrix.adata).__name__
        assert self.count_matrix.path_exists
        assert Path(self.local_path).exists()
        assert self.count_matrix.calculate_file_etag(
            self.adata_path
        ) == self.count_matrix.calculate_file_etag(
            os.path.join(config.LOCAL_DIR, "test", "python.h5ad")
        )

    @mock_s3
    def test_sync_previous_data_not_changed(self):
        self.get_count_matrix_instance()
        self.count_matrix.path_exists = True

        Path(self.local_path).mkdir(parents=True, exist_ok=True)
        shutil.copy(
            os.path.join(config.LOCAL_DIR, "test", "python.h5ad"),
            self.adata_path,
        )

        self.count_matrix.sync()
        assert "AnnData" in type(self.count_matrix.adata).__name__
        assert self.count_matrix.path_exists
        assert Path(self.local_path).exists()
        assert self.count_matrix.calculate_file_etag(
            self.adata_path
        ) == self.count_matrix.calculate_file_etag(
            os.path.join(config.LOCAL_DIR, "test", "python.h5ad")
        )
