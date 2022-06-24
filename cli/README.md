# Solana ETL CLI

Solana ETL lets you convert blockchain data into convenient formats like CSVs and relational databases.

## Quickstart

Install Solana ETL CLI:

```bash
python setup.py install
```

Export blocks and transactions:

```bash
> solanaetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
    --provider-uri https://api.mainnet-beta.solana.com \
    --blocks-output blocks.csv --transactions-output transactions.csv
```

---
