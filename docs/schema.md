# Schema

## blocks.csv

| Column              | Type   |
| ------------------- | ------ |
| number              | bigint |
| height              | bigint |
| previous_block_hash | string |
| timestamp           | bigint |
| transaction_count   | bigint |
| rewards             | json   |
| leader_reward       | bigint |
| leader              | pubkey |

## transactions.csv

| Column              | Type   |
| ------------------- | ------ |
| signature           | string |
| block_hash          | string |
| previous_block_hash | string |
| block_number        | bigint |
| fee                 | bigint |
| status              | string |
| err                 | json   |
| accounts            | json   |
| log_messages        | json   |
| balance_changes     | json   |
| pre_token_balance   | json   |
| post_token_balance  | json   |

## instructions.csv

| Column           | Type   |
| ---------------- | ------ |
| tx_signature     | string |
| index            | bigint |
| parent_index     | bigint |
| accounts         | json   |
| data             | string |
| parsed           | json   |
| program          | string |
| program_id       | string |
| instruction_type | json   |
| params           | json   |

## token_transfers.csv

| Column           | Type   |
| ---------------- | ------ |
| source           | string |
| destionation     | string |
| authority        | string |
| value            | bigint |
| decimals         | bigint |
| mint             | string |
| mint_authority   | string |
| transfer_type    | string |
| tx_signature     | string |

## accounts.csv

| Column                | Type   |
| --------------------- | ------ |
| pubkey                | string |
| tx_signature          | string |
| executable            | bool   |
| lamports              | bigint |
| owner                 | string |
| rent_epoch            | bigint |
| program               | string |
| space                 | bigint |
| account_type          | string |
| is_native             | bool   |
| mint                  | string |
| state                 | string |
| token_amount          | bigint |
| token_amount_decimals | string |
| authorized_voters     | json   |
| prior_voters          | json   |
| node_pubkey           | string |
| epoch_credits         | json   |
| votes                 | json   |
| root_slot             | bigint |
| last_timestamp        | json   |
| data                  | json   |

## tokens.csv

| Column                 | Type   |
| ---------------------- | ------ |
| tx_signature           | string |
| token_type             | string |
| mint                   | string |
| update_authority       | string |
| symbol                 | string |
| uri                    | string |
| seller_fee_basis_point | bigint |
| creators               | json   |
| primary_sale_happened  | bool   |
| is_mutable             | bool   |
