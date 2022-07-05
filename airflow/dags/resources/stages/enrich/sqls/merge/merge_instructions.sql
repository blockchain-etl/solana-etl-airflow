MERGE `{{params.destination_dataset_project_id}}.{{params.destination_dataset_name}}.instructions` dest
USING {{params.dataset_name_temp}}.{{params.source_table}} source
ON FALSE
WHEN NOT MATCHED AND DATE(block_timestamp) = '{{ds}}' THEN
INSERT (
    block_number,
    block_timestamp,
    block_hash,
    tx_signature,
    index,
    parent_index,
    accounts,
    data,
    parsed,
    program,
    program_id,
    instruction_type,
    params
) VALUES (
    block_number,
    block_timestamp,
    block_hash,
    tx_signature,
    index,
    parent_index,
    accounts,
    data,
    parsed,
    program,
    program_id,
    instruction_type,
    params
)
WHEN NOT MATCHED BY source AND DATE(block_timestamp) = '{{ds}}' THEN
DELETE
