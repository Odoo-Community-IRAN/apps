# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import boto3
import logging
import tempfile

from odoo import fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DbBackupConfigure(models.Model):
    _inherit = "db.backup.configure"

    backup_destination = fields.Selection(selection_add=[("custom_s3", "Custom S3")])
    endpoint_url = fields.Char()

    def action_s3cloud(self):
        if self.backup_destination == "custom_s3":
            if self.aws_access_key and self.aws_secret_access_key:
                try:
                    s3_resource = boto3.resource(
                        "s3",
                        aws_access_key_id=self.aws_access_key,
                        aws_secret_access_key=self.aws_secret_access_key,
                        endpoint_url=self.endpoint_url,
                    )
                    bucket = s3_resource.Bucket(self.bucket_file_name)

                    if self.bucket_file_name == bucket.name:
                        self.active = True
                        self.hide_active = True
                        return {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": {
                                "type": "success",
                                "title": _("Connection Test Succeeded!"),
                                "message": _(
                                    "Everything seems properly set up!"
                                ),
                                "sticky": False,
                            }
                        }
                    raise UserError(
                        _("Bucket not found. Please check the bucket name and try again.")
                    )
                except Exception:
                    self.active = False
                    self.hide_active = False
                    return {
                        "type": "ir.actions.client",
                        "tag": "display_notification",
                        "params": {
                            "type": "danger",
                            "title": _("Connection Test Failed!"),
                            "message": _("An error occurred while testing the connection."),
                            "sticky": False,
                        }
                    }
        else:
            super(DbBackupConfigure, self).action_s3cloud()

    def _schedule_auto_backup(self):
        records = self.search([])

        for rec in records:
            backup_time = fields.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = "%s_%s.%s" % (rec.db_name, backup_time, rec.backup_format)
            rec.backup_filename = backup_filename
            
            # Custom S3 Backup
            if rec.backup_destination == "custom_s3":
                if rec.aws_access_key and rec.aws_secret_access_key:
                    try:
                        # Create a boto3 client for Custom S3 with provided
                        # access key id and secret access key
                        s3_resource = boto3.resource(
                            "s3",
                            aws_access_key_id=rec.aws_access_key,
                            aws_secret_access_key=rec.aws_secret_access_key,
                            endpoint_url=rec.endpoint_url,
                        )

                        # If auto_remove is enabled, remove the backups that
                        # are older than specified days from the S3 bucket
                        if rec.auto_remove:
                            bucket = s3_resource.Bucket(rec.bucket_file_name)
                            today = fields.date.today()
                            to_del = {"Objects": []}

                            for my_bucket_object in bucket.objects.all():
                                file_path = my_bucket_object.key
                                date = my_bucket_object.last_modified.date()
                                age_in_days = (today - date).days

                                if age_in_days >= rec.days_to_remove:
                                    to_del["Objects"].append({"Key": file_path})

                            if len(to_del["Objects"]) > 0:
                                bucket.delete_objects(
                                    Bucket=rec.bucket_file_name,
                                    Delete=to_del,
                                )

                        # Create a boto3 resource for Custom S3 with provided
                        # access key id and secret access key
                        s3 = boto3.resource(
                            "s3",
                            aws_access_key_id=rec.aws_access_key,
                            aws_secret_access_key=rec.aws_secret_access_key,
                            endpoint_url=rec.endpoint_url,
                        )

                        # Create a folder in the specified bucket, if it
                        # doesn't already exist
                        s3.Object(rec.bucket_file_name, rec.aws_folder_name + '/').put()
                        bucket = s3.Bucket(rec.bucket_file_name)

                        # Get all the prefixes in the bucket
                        prefixes = set()
                        for obj in bucket.objects.all():
                            key = obj.key
                            if key.endswith('/'):
                                prefix = key[:-1]  # Remove the trailing slash
                                prefixes.add(prefix)

                        # If the specified folder is present in the bucket,
                        # take a backup of the database and upload it to the
                        # S3 bucket
                        if rec.aws_folder_name in prefixes:
                            temp = tempfile.NamedTemporaryFile(suffix=".%s" % rec.backup_format)

                            with open(temp.name, "wb+") as tmp:
                                self.dump_data(rec.db_name, tmp, rec.backup_format)

                            backup_file_path = temp.name
                            remote_file_path = f"{rec.aws_folder_name}/{rec.db_name}_" \
                                               f"{backup_time}.{rec.backup_format}"

                            s3.Object(
                                rec.bucket_file_name,
                                remote_file_path
                            ).upload_file(backup_file_path)
                    except Exception as error:
                        # If any error occurs, set the 'generated_exception'
                        # field to the error message and log the error
                        rec.generated_exception = error
                        _logger.info("Custom S3 Exception: %s", error)
            else:
                super(DbBackupConfigure, self)._schedule_auto_backup()
