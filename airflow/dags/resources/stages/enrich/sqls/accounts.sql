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
    ARRAY(
        SELECT
            STRUCT(
                JSON_EXTRACT(authorized_voter, '$.authorizedVoter') AS authorized_voter,
                CAST(JSON_EXTRACT(authorized_voter, '$.epoch') AS INT64) AS epoch
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(accounts.authorized_voters)) AS authorized_voter 
    ) as authorized_voters,
    accounts.authorized_withdrawer,
    ARRAY(
        SELECT
            STRUCT(
                JSON_EXTRACT(prior_voter, '$.authorizedPubkey') AS authorized_pubkey,
                CAST(JSON_EXTRACT(prior_voter, '$.epochOfLastAuthorizedSwitch') AS INT64) AS epoch_of_last_authorized_switch,
                CAST(JSON_EXTRACT(prior_voter, '$.targetEpoch') AS INT64) AS target_epoch
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(accounts.prior_voters)) AS prior_voter 
    ) as prior_voters,
    accounts.node_pubkey,
    accounts.commission,
    ARRAY(
        SELECT
            STRUCT(
                JSON_EXTRACT(epoch_credit, '$.credits') AS credits,
                CAST(JSON_EXTRACT(epoch_credit, '$.epoch') AS INT64) AS epoch,
                JSON_EXTRACT(epoch_credit, '$.previousCredits') AS previous_credits
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(accounts.epoch_credits)) AS epoch_credit 
    ) as epoch_credits,
    ARRAY(
        SELECT
            STRUCT(
                CAST(JSON_EXTRACT(vote, '$.confirmationCount') AS INT64) AS confirmation_count,
                CAST(JSON_EXTRACT(vote, '$.slot') AS INT64) AS slot
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(accounts.votes)) AS vote 
    ) as votes,
    accounts.root_slot,
    STRUCT(
        CAST(JSON_EXTRACT(accounts.last_timestamp, '$.slot') AS INT64) AS slot,
        TIMESTAMP_SECONDS(CAST(JSON_EXTRACT(accounts.last_timestamp, '$.timestamp') AS INT64)) AS timestamp
    ) AS last_timestamp,
    STRUCT(
        JSON_QUERY(accounts.data, '$.0') AS raw,
        JSON_QUERY(accounts.data, '$.1') AS encoding
    ) AS data
FROM {{params.dataset_name_raw}}.accounts AS accounts
    LEFT JOIN {{params.dataset_name_raw}}.transactions ON transactions.signature = accounts.tx_signature
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}
