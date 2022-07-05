CREATE TEMP FUNCTION parseParams(input STRING)
RETURNS ARRAY<STRUCT<key STRING, value STRING>>
LANGUAGE js AS """
    const parsed = JSON.parse(input)
    return Object.keys(parsed).map(key => {
        let value = parsed[key]
        try {
            let parsedValue = JSON.parse(value)
            if (parsedValue instanceof Array) {
                value = parsedValue.join(',')
            } else if (parsedValue instanceof Object) {
                value = JSON.stringify(parsedValue)
            }
        } catch {}
        return {
            key,
            value
        }
    });
""";

SELECT
    transactions.block_number,
    TIMESTAMP_SECONDS(transactions.block_timestamp) AS block_timestamp,
    transactions.block_hash,
    instructions.tx_signature,
    instructions.index,
    instructions.parent_index,
    JSON_EXTRACT_ARRAY(instructions.accounts) AS accounts,
    instructions.data,
    instructions.parsed,
    instructions.program,
    instructions.program_id,
    instructions.instruction_type,
    parseParams(instructions.params) AS params
FROM {{params.dataset_name_raw}}.instructions AS instructions
    LEFT JOIN {{params.dataset_name_raw}}.transactions ON transactions.signature = instructions.tx_signature
WHERE true
    {% if not params.load_all_partitions %}
    AND DATE(TIMESTAMP_SECONDS(transactions.block_timestamp)) = '{{ds}}'
    {% endif %}
