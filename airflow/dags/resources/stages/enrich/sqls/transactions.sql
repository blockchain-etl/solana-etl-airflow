SELECT
    transactions.signature,
    transactions.block_hash,
    transactions.previous_block_hash,
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.fee,
    transactions.status,
    transactions.err,
    ARRAY(
        SELECT
            STRUCT(
                JSON_EXTRACT(account, '$.pubkey') AS pubkey,
                CAST(JSON_EXTRACT(account, '$.signer') AS BOOL) AS signer,
                CAST(JSON_EXTRACT(account, '$.writable') AS BOOL) AS writable
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(transactions.accounts)) AS account 
    ) as accounts,
    JSON_EXTRACT_ARRAY(transactions.log_messages) AS log_messages,
    ARRAY(
        SELECT
            STRUCT(
                JSON_EXTRACT(balance_change, '$.account') AS account,
                CAST(JSON_EXTRACT(balance_change, '$.before') AS NUMERIC) AS before,
                CAST(JSON_EXTRACT(balance_change, '$.after') AS NUMERIC) AS after
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(transactions.balance_changes)) AS balance_change 
    ) as balance_changes,
    ARRAY(
        SELECT
            STRUCT(
                CAST(JSON_EXTRACT(pre_token_balance, '$.accountIndex') AS INT64) AS account_index,
                JSON_EXTRACT(pre_token_balance, '$.mint') AS mint,
                JSON_EXTRACT(pre_token_balance, '$.owner') AS owner,
                CAST(JSON_EXTRACT_SCALAR(pre_token_balance, '$.uiTokenAmount.amount') AS NUMERIC) AS amount,
                CAST(JSON_EXTRACT_SCALAR(pre_token_balance, '$.uiTokenAmount.decimals') AS INT64) AS decimals
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(transactions.pre_token_balances)) AS pre_token_balance 
    ) as pre_token_balances,
    ARRAY(
        SELECT
            STRUCT(
                CAST(JSON_EXTRACT(post_token_balance, '$.accountIndex') AS INT64) AS account_index,
                JSON_EXTRACT(post_token_balance, '$.mint') AS mint,
                JSON_EXTRACT(post_token_balance, '$.owner') AS owner,
                CAST(JSON_EXTRACT_SCALAR(post_token_balance, '$.uiTokenAmount.amount') AS NUMERIC) AS amount,
                CAST(JSON_EXTRACT_SCALAR(post_token_balance, '$.uiTokenAmount.decimals') AS INT64) AS decimals
            )
        FROM
            UNNEST(JSON_EXTRACT_ARRAY(transactions.post_token_balances)) AS post_token_balance 
    ) as post_token_balances,
FROM {{params.dataset_name_raw}}.transactions AS transactions
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}
