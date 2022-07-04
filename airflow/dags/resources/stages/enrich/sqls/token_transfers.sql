SELECT
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.block_hash,
    token_transfers.source,
    token_transfers.destination,
    token_transfers.authority,
    token_transfers.value,
    token_transfers.decimals,
    token_transfers.mint,
    token_transfers.mint_authority,
    token_transfers.transfer_type,
    token_transfers.tx_signature,
FROM {{params.dataset_name_raw}}.token_transfers AS token_transfers
    LEFT JOIN {{params.dataset_name_raw}}.transactions ON transactions.signature = token_transfers.tx_signature
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}
