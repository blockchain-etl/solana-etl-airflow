MERGE `{{params.destination_dataset_project_id}}.{{params.destination_dataset_name}}.token_transfers` dest
USING {{params.dataset_name_temp}}.{{params.source_table}} source
ON FALSE
WHEN NOT MATCHED AND DATE(block_timestamp) = '{{ds}}' THEN
INSERT (
    block_number,
    block_timestamp,
    block_hash,
    tx_signature,
    source,
    destination,
    authority,
    value
) VALUES (
    block_number,
    block_timestamp,
    block_hash,
    tx_signature,
    source,
    destination,
    authority,
    value
)
WHEN NOT MATCHED BY source AND DATE(block_timestamp) = '{{ds}}' THEN
DELETE
