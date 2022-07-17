SELECT IF(
(
    SELECT COUNT(*) FROM `{{params.destination_dataset_project_id}}.{{params.dataset_name}}.blocks`
    WHERE DATE(timestamp) = '{{ds}}'
) > 0, 1, 0
