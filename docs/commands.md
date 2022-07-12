# Commands

All the commands accept `-h` parameter for help, e.g.:

```bash
> solanaetl export_blocks_and_transactions -h

Usage: solanaetl export_blocks_and_transactions [OPTIONS]

  Exports blocks and transactions.

Options:
  -s, --start-block INTEGER   Start block  [default: 0]
  -e, --end-block INTEGER     End block  [required]
  -b, --batch-size INTEGER    The number of blocks to export at a time.
                              [default: 1]
  -p, --provider-uri TEXT     The URI of the web3 provider e.g.
                              https://api.mainnet-beta.solana.com  [default:
                              https://api.mainnet-beta.solana.com]
  -w, --max-workers INTEGER   The maximum number of workers.  [default: 5]
  --blocks-output TEXT        The output file for blocks. If not provided
                              blocks will not be exported. Use "-" for stdout
  --transactions-output TEXT  The output file for transactions. If not
                              provided transactions will not be exported. Use
                              "-" for stdout.
  --instructions-output TEXT  The output file for instructions. If not
                              provided instructions will not be exported. Use
                              "-" for stdout.
  -h, --help                  Show this message and exit
```

For the `--output` parameters the supported types are csv and json. The format type is inferred from the output file name.

## export_blocks_and_transactions

```bash
> solanaetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
    --blocks-output blocks.csv \
    --transactions-output transactions.csv \
    --instructions-output instructions.csv
```

Omit `--blocks-output` or `--transactions-output` or `--instructions-output` options if you want to export only instructions/transactions/blocks.

You can tune `--batch-size`, `--max-workers` for performance.

[Blocks, transactions and instructions schema](schema.md#blockscsv).

## extract_token_transfers

First export instructions with [export_blocks_and_transactions](#export_blocks_and_transactions)

```bash
> solanaetl extract_token_transfers \
    -i ./instructions.csv \
    -o token_transfers.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

[Token transfers schema](schema.md#token_transferscsv).

## extract_accounts

First export transactions with [export_blocks_and_transactions](#export_blocks_and_transactions)

```bash
> solanaetl extract_accounts \
    -t ./transactions.csv \
    -o accounts.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

[Accounts schema](schema.md#accountscsv).

## extract_tokens

First export accounts with [extract_accounts](#extract_accounts)

```bash
> solanaetl extract_tokens \
    -a ./accounts.csv \
    -o tokens.csv
```

You can tune `--batch-size`, `--max-workers` for performance.

[Tokens schema](schema.md#tokenscsv).
