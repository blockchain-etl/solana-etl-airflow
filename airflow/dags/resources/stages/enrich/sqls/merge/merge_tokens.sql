MERGE `{{params.destination_dataset_project_id}}.{{params.destination_dataset_name}}.tokens` dest
USING {{params.dataset_name_temp}}.{{params.source_table}} source
ON FALSE
WHEN NOT MATCHED AND DATE(block_timestamp) = '{{ds}}' THEN
INSERT (
    block_number,
    block_timestamp,
    block_hash,
    tx_signature,
    mint,
    update_authority,
    name,
    symbol,
    uri,
    seller_fee_basis_points,
    creators,
    primary_sale_happened,
    is_mutable
) VALUES (
    block_number,
    block_timestamp,
    block_hash,
    tx_signature,
    mint,
    update_authority,
    name,
    symbol,
    uri,
    seller_fee_basis_points,
    creators,
    primary_sale_happened,
    is_mutable
)
WHEN NOT MATCHED BY source AND DATE(block_timestamp) = '{{ds}}' THEN
DELETE
