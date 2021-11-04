"""Provide an s3 interface."""
import logging
import os
import sys
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from hypha.core.auth import login_optional
from hypha.utils import (
    safe_join,
    list_objects_sync,
)
from hypha.s3 import FSFileResponse

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger("rdf")
logger.setLevel(logging.INFO)


class RDFController:
    """Represent an RDF controller."""

    # pylint: disable=too-many-statements

    def __init__(
        self,
        core_interface,
        s3_controller=None,
        rdf_bucket="hypha-apps",
    ):
        """Set up controller."""
        self.event_bus = core_interface.event_bus
        self.s3_controller = s3_controller
        self.core_interface = core_interface
        self.rdf_bucket = rdf_bucket

        self.s3client = self.s3_controller.create_client_sync()

        try:
            self.s3client.create_bucket(Bucket=self.rdf_bucket)
            logger.info("Bucket created: %s", self.rdf_bucket)
        except self.s3client.exceptions.BucketAlreadyExists:
            pass
        except self.s3client.exceptions.BucketAlreadyOwnedByYou:
            pass

        router = APIRouter()

        @router.get("/public/rdfs/{path:path}")
        async def get_app_file(
            path: str,
            request: Request,
            user_info: login_optional = Depends(login_optional),
        ):
            try:
                path = safe_join(path)
                return FSFileResponse(
                    self.s3_controller.create_client_async(), self.rdf_bucket, path
                )
            except ClientError:
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "detail": f"File does not exists: {path}",
                    },
                )

        core_interface.register_router(router)
        core_interface.register_service_as_root(self.get_rdf_service())

    def save(self, name, source):
        """Save an RDF."""
        user_info = self.core_interface.current_user.get()
        response = self.s3client.put_object(
            ACL="public-read",
            Body=source,
            Bucket=self.rdf_bucket,
            Key=f"{user_info.id}/{name}",
        )
        assert (
            "ResponseMetadata" in response
            and response["ResponseMetadata"]["HTTPStatusCode"] == 200
        ), f"Failed to deploy app: {name}"
        self.event_bus.emit("rdf_added", f"{user_info.id}/{name}")

    def remove(self, name):
        """Remove an RDF."""
        user_info = self.core_interface.current_user.get()
        response = self.s3client.delete_object(
            Bucket=self.rdf_bucket,
            Key=f"{user_info.id}/{name}",
        )
        assert (
            "ResponseMetadata" in response
            and response["ResponseMetadata"]["HTTPStatusCode"] == 204
        ), f"Failed to undeploy app: {name}"
        self.event_bus.emit("rdf_removed", f"{user_info.id}/{name}")

    def list(self, user: str = None):
        """List all the RDFs."""
        items = list_objects_sync(
            self.s3client, self.rdf_bucket, prefix=user, delimeter=""
        )
        ret = []
        for item in items:
            if item["type"] == "directory":
                continue
            parts = os.path.split(item["name"])
            user = parts[0]
            name = "/".join(parts[1:])
            ret.append(
                {"name": name, "user": user, "url": f"public/rdfs/{user}/{name}"}
            )
        return ret

    def get_rdf_service(self):
        """Get rdf controller."""
        return {
            "_rintf": True,
            "name": "rdf",
            "type": "rdf",
            "save": self.save,
            "remove": self.remove,
            "list": self.list,
        }