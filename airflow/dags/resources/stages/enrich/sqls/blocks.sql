SELECT
    blocks.number,
    blocks.height,
    blocks.hash,
    blocks.previous_block_hash,
    TIMESTAMP_SECONDS(blocks.timestamp) AS timestamp,
    blocks.transaction_count,
    blocks.rewards,
    blocks.leader_reward,
    blocks.leader
FROM {{params.dataset_name_raw}}.blocks AS blocks
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(blocks.timestamp)) = '{{ds}}'
    {% endif %}
