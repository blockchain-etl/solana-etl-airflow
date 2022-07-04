MERGE `{{params.destination_dataset_project_id}}.{{params.destination_dataset_name}}.blocks` dest
USING {{params.dataset_name_temp}}.{{params.source_table}} source
ON FALSE
WHEN NOT MATCHED AND DATE(timestamp) = '{{ds}}' THEN
INSERT (
    number,
    height,
    `hash`,
    previous_block_hash,
    timestamp,
    transaction_count,
    rewards,
    leader_reward,
    leader
) VALUES (
    number,
    height,
    `hash`,
    previous_block_hash,
    timestamp,
    transaction_count,
    rewards,
    leader_reward,
    leader
)
WHEN NOT MATCHED BY source AND DATE(timestamp) = '{{ds}}' THEN
DELETE
