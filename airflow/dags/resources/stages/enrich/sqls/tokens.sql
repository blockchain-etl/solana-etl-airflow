SELECT
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.block_hash,
    tokens.tx_signature,
    tokens.token_type,
    tokens.mint,
    tokens.update_authority,
    tokens.name,
    tokens.symbol,
    tokens.uri,
    tokens.seller_fee_basis_points,
    ARRAY(
        SELECT
            STRUCT(
                JSON_EXTRACT(creator, '$.address') AS address,
                CAST(JSON_EXTRACT(creator, '$.verified') AS INT64) AS verified,
                CAST(JSON_EXTRACT(creator, '$.share') AS INT64) AS share
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(tokens.creators)) AS creator 
    ) as creators,
    tokens.primary_sale_happened,
    tokens.is_mutable
FROM {{params.dataset_name_raw}}.tokens AS tokens
    LEFT JOIN {{params.dataset_name_raw}}.transactions ON transactions.signature = tokens.tx_signature
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}