SELECT
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
WHERE true
