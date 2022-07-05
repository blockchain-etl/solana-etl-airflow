MERGE `{{params.destination_dataset_project_id}}.{{params.destination_dataset_name}}.transactions` dest
USING {{params.dataset_name_temp}}.{{params.source_table}} source
ON FALSE
WHEN NOT MATCHED AND DATE(block_timestamp) = '{{ds}}' THEN
INSERT (
    signature,
    block_hash,
    previous_block_hash,
    block_number,
    block_timestamp,
    fee,
    status,
    err,
    accounts,
    log_messages,
    balance_changes,
    pre_token_balances,
    post_token_balances
) VALUES (
    signature,
    block_hash,
    previous_block_hash,
    block_number,
    block_timestamp,
    fee,
    status,
    err,
    accounts,
    log_messages,
    balance_changes,
    pre_token_balances,
    post_token_balances
)
WHEN NOT MATCHED BY source AND DATE(block_timestamp) = '{{ds}}' THEN
DELETE
