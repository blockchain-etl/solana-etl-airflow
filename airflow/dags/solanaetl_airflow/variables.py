# The MIT License (MIT)
# Copyright (c) 2022 Gamejam.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from datetime import datetime

from airflow.models import Variable


def read_export_dag_vars(var_prefix, **kwargs):
    """Read Airflow variables for Export DAG"""
    export_start_block = int(read_var(
        'export_start_block', var_prefix, True, **kwargs))

    export_end_block = read_var(
        'export_end_block', var_prefix, False, **kwargs)
    export_end_block = int(
        export_end_block) if export_end_block is not None else export_start_block+1

    provider_uris = read_var('provider_uris', var_prefix, True, **kwargs)
    provider_uris = [uri.strip() for uri in provider_uris.split(',')]

    export_max_active_runs = read_var(
        'export_max_active_runs', var_prefix, False, **kwargs)
    export_max_active_runs = int(
        export_max_active_runs) if export_max_active_runs is not None else None

    vars = {
        'output_bucket': read_var('output_bucket', var_prefix, True, **kwargs),
        'export_start_block': export_start_block,
        'export_end_block': export_end_block,
        'export_schedule_interval': read_var('export_schedule_interval', var_prefix, True, **kwargs),
        'provider_uris': provider_uris,
        'notification_emails': read_var('notification_emails', None, False, **kwargs),
        'export_max_active_runs': export_max_active_runs,
        'export_max_workers': int(read_var('export_max_workers', var_prefix, True, **kwargs)),
    }

    return vars


def read_load_dag_vars(var_prefix, **kwargs):
    """Read Airflow variables for Load DAG"""
    load_start_block = int(read_var(
        'export_start_block', var_prefix, True, **kwargs))

    load_end_block = read_var(
        'export_end_block', var_prefix, False, **kwargs)
    load_end_block = int(
        load_end_block) if load_end_block is not None else load_start_block+1

    output_bucket = read_var('output_bucket', var_prefix, True, **kwargs)
    checkpoint_bucket = read_var(
        'checkpoint_bucket', var_prefix, False, **kwargs)
    if not checkpoint_bucket:
        checkpoint_bucket = output_bucket
    vars = {
        'output_bucket': output_bucket,
        'checkpoint_bucket': checkpoint_bucket,
        'load_start_block': load_start_block,
        'load_end_block': load_end_block,
        'destination_dataset_project_id': read_var('destination_dataset_project_id', var_prefix, True, **kwargs),
        'notification_emails': read_var('notification_emails', None, False, **kwargs),
        'load_schedule_interval': read_var('load_schedule_interval', var_prefix, True, **kwargs),
        'load_all_partitions': parse_bool(read_var('load_all_partitions', var_prefix, False, **kwargs), default=None),
    }

    return vars


def read_parse_dag_vars(var_prefix, dataset, **kwargs):
    per_dataset_var_prefix = var_prefix + dataset + '_'
    vars = {
        'parse_destination_dataset_project_id': read_var('parse_destination_dataset_project_id', var_prefix, True, **kwargs),
        'schedule_interval': read_var('schedule_interval', var_prefix, True, **kwargs),
        'parse_all_partitions': parse_bool(read_var('parse_all_partitions', per_dataset_var_prefix, False), default=None),
        'notification_emails': read_var('notification_emails', None, False, **kwargs),
    }

    parse_start_date = read_var('parse_start_date', vars, False, **kwargs)
    if parse_start_date is not None:
        parse_start_date = datetime.strptime(parse_start_date, '%Y-%m-%d')
        vars['parse_start_date'] = parse_start_date

    return vars


def read_verify_streaming_dag_vars(var_prefix, **kwargs):
    vars = {
        'destination_dataset_project_id': read_var('destination_dataset_project_id', var_prefix, True, **kwargs),
        'notification_emails': read_var('notification_emails', None, False, **kwargs),
    }

    max_lag_in_minutes = read_var(
        'max_lag_in_minutes', var_prefix, False, **kwargs)
    if max_lag_in_minutes is not None:
        vars['max_lag_in_minutes'] = max_lag_in_minutes

    return vars


def read_var(var_name, var_prefix=None, required=False, **kwargs):
    """Read Airflow variable"""
    full_var_name = f'{var_prefix}{var_name}' if var_prefix is not None else var_name
    var = Variable.get(full_var_name, '')
    var = var if var != '' else None
    if var is None:
        var = kwargs.get(var_name)
    if required and var is None:
        raise ValueError(f'{full_var_name} variable is required')
    return var


def parse_bool(bool_string, default=True):
    if isinstance(bool_string, bool):
        return bool_string
    if bool_string is None or len(bool_string) == 0:
        return default
    else:
        return bool_string.lower() in ["true", "yes"]
