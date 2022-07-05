SELECT
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.block_hash,
    nfts.tx_signature,
    nfts.mint,
    nfts.update_authority,
    nfts.name,
    nfts.symbol,
    nfts.uri,
    nfts.seller_fee_basis_points,
    nfts.creators,
    nfts.primary_sale_happened,
    nfts.is_mutable
FROM {{params.dataset_name_raw}}.nfts AS nfts
    LEFT JOIN {{params.dataset_name_raw}}.transactions ON transactions.signature = nfts.tx_signature
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}