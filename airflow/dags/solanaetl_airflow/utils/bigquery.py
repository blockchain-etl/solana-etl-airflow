import json
import logging


def submit_bigquery_job(job, configuration):
    try:
        logging.info('Creating a job: ' +
                     json.dumps(configuration.to_api_repr()))
        result = job.result()
        logging.info(result)
        assert job.errors is None or len(job.errors) == 0
        return result
    except Exception:
        logging.info(job.errors)
        raise
