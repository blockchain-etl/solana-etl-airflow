SELECT IF(
(
    SELECT MAX(height)
    FROM `{{params.destination_dataset_project_id}}.{{params.dataset_name}}.blocks`
    WHERE DATE(TIMESTAMP) <= '{{ds}}'
) + 1 =
(
    SELECT COUNT(*) FROM `{{params.destination_dataset_project_id}}.{{params.dataset_name}}.blocks`
    WHERE DATE(TIMESTAMP) <= '{{ds}}'
), 1, 0