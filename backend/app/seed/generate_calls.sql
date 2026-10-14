WITH planned AS (
    SELECT *
    FROM unnest(
        CAST(:hour_starts AS timestamptz[]),
        CAST(:campaign_ids AS int[]),
        CAST(:call_counts AS int[]),
        CAST(:missed_thresholds AS float8[]),
        CAST(:converted_thresholds AS float8[])
    ) AS plan (hour_start, campaign_id, call_count, missed_threshold, converted_threshold)
),
generated AS (
    SELECT
        planned.hour_start + random() * INTERVAL '1 hour' AS started_at,
        planned.campaign_id,
        CASE
            WHEN dice.roll < planned.missed_threshold THEN 'missed'
            WHEN dice.roll < planned.converted_threshold THEN 'converted'
            ELSE 'connected'
        END::call_status AS status
    FROM planned
    CROSS JOIN LATERAL (SELECT random() AS roll FROM generate_series(1, planned.call_count)) AS dice
),
timed AS (
    SELECT
        generated.*,
        CASE status
            WHEN 'missed' THEN 0
            WHEN 'converted' THEN 120 + floor(random() * 780)::int
            ELSE 20 + floor(random() * 400)::int
        END AS duration_seconds
    FROM generated
)
INSERT INTO calls (started_at, account_id, campaign_id, caller_number, duration_seconds, ended_at, status)
SELECT
    started_at,
    :account_id,
    campaign_id,
    '+1555' || lpad(floor(random() * 10000000)::int::text, 7, '0'),
    duration_seconds,
    started_at + duration_seconds * INTERVAL '1 second',
    status
FROM timed
