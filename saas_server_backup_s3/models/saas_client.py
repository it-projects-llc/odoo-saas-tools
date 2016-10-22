# -*- coding: utf-8 -*-
import os
import sys
from multiprocessing.pool import Pool
import multiprocessing
import tempfile
import base64
from tempfile import NamedTemporaryFile
import math

from odoo import _
from odoo import api
from odoo import exceptions
from odoo import models
import psycopg2

import logging
_logger = logging.getLogger(__name__)


try:
    import boto
    from boto.s3.key import Key
except:
    _logger.debug('SAAS Sysadmin Bacnkup Agent S3 Requires the python library Boto which is not \
    found on your installation')


try:
    parallel_upload = False
    from filechunkio import FileChunkIO
    parallel_upload = True
except:
    _logger.debug('SAAS Sysadmin Bacnkup Agent S3 performs better with large '
                  'files if you have FileChunkIO installed')


def _get_s3_conn(env):
    ir_params = env['ir.config_parameter']
    aws_access_key_id = ir_params.get_param('saas_s3.saas_s3_aws_accessid')
    aws_secret_access_key = ir_params.get_param('saas_s3.saas_s3_aws_accesskey')
    aws_s3_bucket = ir_params.get_param('saas_s3.saas_s3_aws_bucket')
    if not aws_access_key_id or not aws_secret_access_key or not aws_s3_bucket:
        raise exceptions.Warning( _(u'Please provide your AWS Access Key and ID \
        and also the S3 bucket to be used'))
    return boto.connect_s3(aws_access_key_id, aws_secret_access_key), aws_s3_bucket


def _upload_part(bucketname, aws_key, aws_secret, multipart_id, part_num,
                 source_path, offset, bytes, amount_of_retries=10):
    """
    Uploads a part with retries.
    based on http://www.topfstedt.de/python-parallel-s3-multipart-upload-with-retries.html
    """
    def _upload(retries_left=amount_of_retries):
        try:
            _logger.info('Start uploading part # %d ...' % part_num)
            conn = boto.connect_s3(aws_key, aws_secret)
            bucket = conn.get_bucket(bucketname)
            for mp in bucket.get_all_multipart_uploads():
                if mp.id == multipart_id:
                    with FileChunkIO(source_path, 'r', offset=offset,
                                     bytes=bytes) as fp:
                        mp.upload_part_from_file(fp=fp, part_num=part_num)
                    break
        except Exception as exc:
            if retries_left:
                _upload(retries_left=retries_left - 1)
            else:
                logging.info('... Failed uploading part # %d' % part_num)
                raise exc
        else:
            logging.info('... Uploaded part # %d' % part_num)

    _upload()


class SaasServerClient(models.Model):
    _inherit = 'saas_server.client'

    def upload(myfile):
        bucket = conn.get_bucket("parallel_upload_tests")
        key = bucket.new_key(myfile).set_contents_from_string('some content')
        return myfile

    @staticmethod
    def _transport_backup_simple(conn, bucket_name, data, filename):
        _logger.info('Backing up via S3 simple agent')
        bucket = conn.get_bucket(bucket_name)
        k = Key(bucket)
        k.key = filename
        k.set_contents_from_string(data)
        _logger.info('Data successfully backed up to s3')

    @staticmethod
    def _transport_backup_parallel(data, filename, aws_key, aws_secret, bucketname):
        """
        Parallel multipart upload.
        """
        headers = {}
        _logger.info('Backing up via S3 parallel multipart upload agent')
        keyname = filename
        tempInFile = NamedTemporaryFile(suffix='.zip', prefix='db-backup-', delete=False)
        tempInFile.write(data)
        tempInFile.close()
        source_path = tempInFile.name
        source_size = os.stat(source_path).st_size
        parallel_processes = (multiprocessing.cpu_count() * 2) + 1

        conn = boto.connect_s3(aws_key, aws_secret)
        bucket = conn.get_bucket(bucketname)

        mtype = 'application/zip, application/octet-stream'
        headers.update({'Content-Type': mtype})

        mp = bucket.initiate_multipart_upload(keyname, headers=headers)

        bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(source_size)),
                              5242880)
        chunk_amount = int(math.ceil(source_size / float(bytes_per_chunk)))

        pool = Pool(processes=parallel_processes)
        for i in range(chunk_amount):
            offset = i * bytes_per_chunk
            remaining_bytes = source_size - offset
            bytes = min([bytes_per_chunk, remaining_bytes])
            part_num = i + 1
            pool.apply_async(_upload_part, [bucketname, aws_key, aws_secret, mp.id,
                                            part_num, source_path, offset, bytes])
        pool.close()
        pool.join()

        if len(mp.get_all_parts()) == chunk_amount:
            mp.complete_upload()
        else:
            mp.cancel_upload()
        os.unlink(tempInFile.name)
        _logger.info('Data successfully backed up to s3')

    @api.model
    def _transport_backup(self, dump_db, filename=None):
        '''
        send db dump to S3
        '''
        with tempfile.TemporaryFile() as t:
            dump_db(t)
            t.seek(0)
            db_dump = base64.b64decode(t.read().encode('base64'))

        if parallel_upload and sys.getsizeof(db_dump) > 5242880:
            ir_params = self.env['ir.config_parameter']
            aws_key = ir_params.get_param('saas_s3.saas_s3_aws_accessid')
            aws_secret = ir_params.get_param('saas_s3.saas_s3_aws_accesskey')
            bucketname = ir_params.get_param('saas_s3.saas_s3_aws_bucket')
            self._transport_backup_parallel(db_dump, filename, aws_key, aws_secret, bucketname)
        else:
            conn, bucket_name = _get_s3_conn(self.env)
            self._transport_backup_simple(conn, bucket_name, db_dump, filename)

        return True
