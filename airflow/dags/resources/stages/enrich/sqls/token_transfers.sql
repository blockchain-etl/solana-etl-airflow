SELECT
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.block_hash,
    token_transfers.tx_signature,
    token_transfers.source,
    token_transfers.destination,
    token_transfers.authority,
    token_transfers.value
FROM {{params.dataset_name_raw}}.token_transfers AS token_transfers
    LEFT JOIN {{params.dataset_name_raw}}.transactions ON transactions.signature = token_transfers.tx_signature
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}
