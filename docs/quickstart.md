# Quickstart

Install Solana ETL:

```bash
pip3 install solana-etl
```

Export blocks, transactions and instructions:

```bash
> solanaetl export_blocks_and_transactions \
    --start-block 0 \
    --end-block 500000 \
    --blocks-output blocks.csv \
    --transactions-output transactions.csv \
    --instructions-output instructions.csv
```

Find all commands [here](commands.md).

---

To run the latest version of Solana ETL, check out the repo and call

```bash
> cd cli
> pip3 install -e .
> python3 solanaetl.py
```
