SELECT
    transactions.signature,
    transactions.block_hash,
    transactions.previous_block_hash,
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.fee,
    transactions.status,
    transactions.err,
    transactions.accounts,
    transactions.log_messages,
    transactions.balance_changes,
    transactions.pre_token_balances,
    transactions.post_token_balances
FROM {{params.dataset_name_raw}}.transactions AS transactions
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}
