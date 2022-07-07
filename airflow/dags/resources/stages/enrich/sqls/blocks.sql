SELECT
    blocks.number,
    blocks.height,
    blocks.hash,
    blocks.previous_block_hash,
    TIMESTAMP_SECONDS(blocks.timestamp) AS timestamp,
    blocks.transaction_count,
    ARRAY(
        SELECT
            STRUCT(
                CAST(JSON_EXTRACT(reward, '$.commission') AS NUMERIC) AS commission,
                CAST(JSON_EXTRACT(reward, '$.lamports') AS NUMERIC) AS lamports,
                CAST(JSON_EXTRACT(reward, '$.postBalance') AS NUMERIC) AS post_balance,
                JSON_EXTRACT(reward, '$.pubkey') AS pubkey,
                JSON_EXTRACT(reward, '$.rewardType') AS reward_type
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(blocks.rewards)) AS reward 
    ) as rewards,
    blocks.leader_reward,
    blocks.leader
FROM {{params.dataset_name_raw}}.blocks AS blocks
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(blocks.timestamp)) = '{{ds}}'
    {% endif %}
