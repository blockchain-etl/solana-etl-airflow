# Solana ETL CLI

Solana ETL lets you convert blockchain data into convenient formats like CSVs and relational databases.

## Quickstart

Install Solana ETL CLI:

```bash
cd cli
python setup.py install
```

---
Environment:

```bash
> export SERUM_DEX_V3 = "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin"
> export METADATA_PROGRAM_ID = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
```

---

Export all

```bash
> solanaetl export_all \
    --start 138802069 \
    --end 138802069 \
    --output-dir=./output
```

---

Export blocks and transactions (include input accounts, instructions):

```bash
> solanaetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
    --blocks-output blocks.csv \
    --transactions-output transactions.csv \
    --instructions-output instructions.csv
```

---

Export instructions:

```bash
> solanaetl extract_field -i transactions.csv -o transaction_signatures.txt -f signature
> solanaetl export_instructions \
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
    -t ./transactions.csv \
    -o accounts.csv
```

---

Export tokens:

```bash
> solanaetl extract_tokens \
    -a ./accounts.csv \
    -o tokens.csv
```

## Test

```bash
> python -m pip install -r requirements_test.txt
> python -m pytest
```
