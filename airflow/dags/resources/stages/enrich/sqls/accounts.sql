SELECT
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.block_hash,
    accounts.pubkey,
    accounts.tx_signature,
    accounts.executable,
    accounts.lamports,
    accounts.owner,
    accounts.rent_epoch,
    accounts.program,
    accounts.space,
    accounts.account_type,
    accounts.is_native,
    accounts.mint,
    accounts.state,
    accounts.token_amount,
    accounts.token_amount_decimals,
    accounts.program_data,
    accounts.authorized_voters,
    accounts.authorized_withdrawer,
    accounts.prior_voters,
    accounts.node_pubkey,
    accounts.commission,
    accounts.epoch_credits,
    accounts.votes,
    accounts.root_slot,
    accounts.last_timestamp,
    accounts.data
FROM {{params.dataset_name_raw}}.accounts AS accounts
    LEFT JOIN {{params.dataset_name_raw}}.transactions ON transactions.signature = accounts.tx_signature
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}
