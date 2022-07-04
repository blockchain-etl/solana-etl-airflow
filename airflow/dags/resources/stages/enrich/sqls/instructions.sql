SELECT
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.block_hash,
    instructions.tx_signature,
    instructions.index,
    instructions.parent_index,
    instructions.accounts,
    instructions.data,
    instructions.parsed,
    instructions.program,
    instructions.program_id,
    instructions.instruction_type,
    instructions.params
FROM {{params.dataset_name_raw}}.instructions AS instructions
    LEFT JOIN {{params.dataset_name_raw}}.transactions ON transactions.signature = instructions.tx_signature
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}
