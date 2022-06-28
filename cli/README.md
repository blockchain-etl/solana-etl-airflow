# Solana ETL CLI

Solana ETL lets you convert blockchain data into convenient formats like CSVs and relational databases.

## Quickstart

Install Solana ETL CLI:

```bash
python setup.py install
```

Export blocks and transactions (include input accounts, instructions):

```bash
> solanaetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
    --provider-uri https://api.mainnet-beta.solana.com \
    --blocks-output blocks.csv \
    --transactions-output transactions.csv \
    --instructions-output instructions.csv
```

---

Export instructions:

```bash
> solanaetl extract_field -i transactions.csv -o transaction_signatures.txt -f signature
> solanaetl export_instructions \
    --provider-uri https://api.mainnet-beta.solana.com \
    -t ./transaction_signatures.txt \
    -o instructions.csv
```

---

Extract token transfer:

```bash
> solanaetl extract_token_transfers \
    -i ./instructions.csv \
    -o token_transfers.csv
```

---

Export accounts:

```bash
> solanaetl extract_accounts \
    --provider-uri https://api.mainnet-beta.solana.com \
    -t ./transactions.csv \
    -o accounts.csv
```