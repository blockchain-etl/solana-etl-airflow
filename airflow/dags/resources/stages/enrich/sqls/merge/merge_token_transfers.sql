MERGE `{{params.destination_dataset_project_id}}.{{params.destination_dataset_name}}.token_transfers` dest
USING {{params.dataset_name_temp}}.{{params.source_table}} source
ON FALSE
WHEN NOT MATCHED AND DATE(block_timestamp) = '{{ds}}' THEN
INSERT (
    block_number,
    block_timestamp,
    block_hash,
    source,
    destination,
    authority,
    value,
    decimals,
    mint,
    mint_authority,
    transfer_type,
    tx_signature
) VALUES (
    block_number,
    block_timestamp,
    block_hash,
    source,
    destination,
    authority,
    value,
    decimals,
    mint,
    mint_authority,
    transfer_type,
    tx_signature
)
WHEN NOT MATCHED BY source AND DATE(block_timestamp) = '{{ds}}' THEN
DELETE
