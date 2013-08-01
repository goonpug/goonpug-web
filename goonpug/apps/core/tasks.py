# -*- coding: utf-8 -*-
# Copyright (c) 2013 Peter Rowlands
# All rights reserved.

import hashlib
from zipfile import ZipFile, BadZipFile

from django.core.exceptions import SuspiciousFileOperation
from queued_storage.tasks import Transfer

from .models import MatchMap
from ..libs.goonpugd import parse_match_log


class TransferMatchZip(Transfer):
    """
    Transfer a goonpug match zip file to S3 and parse the match logs.
    """

    def transfer(self, name, local, remote, **kwargs):
        """Parses and transfers the log if it does not already
        exist in our DB

        Returns:
            True if the transfer was successful or skipped
            False if the transfer should be retried
        """
        try:
            result = True
            zf = ZipFile(local(name), 'r')
            m = self.process_zip(zf)
            zf.close()
            if not m.zip_url:
                # If we haven't uploaded this yet
                result = super(TransferMatchZip, self).transfer(
                    name, local, remote, **kwargs)
                if result:
                    m.zip_url = remote.url(name)
                    m.save()
            if result:
                local.delete(name)
            return result
        except BadZipFile:
            local.delete(name)
            raise SuspiciousFileOperation

    def process_zip(self, zf):
        """Validate and process a match zip file

        Returns:
            The MatchMap object for this match
        """
        sha = hashlib.sha1()
        names = sorted(zf.namelist())
        has_demo = False
        log_data = ''
        for name in names:
            if name.endswith('.dem'):
                has_demo = True
            elif name.endswith('.log'):
                data = zf.read(name)
                sha.update(data)
                log_data += data
        digest = sha.hexdigest()
        try:
            return MatchMap.objects.get(sha1sum=digest)
        except MatchMap.DoesNotExist:
            m = parse_match_log(log_data)
            if m:
                m.has_demo = has_demo
                m.save()
            return m
