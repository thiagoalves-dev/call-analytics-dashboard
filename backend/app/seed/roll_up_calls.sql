INSERT INTO call_stats_hourly (account_id, bucket, campaign_id, total, missed, connected, converted, duration_seconds)
SELECT
    account_id,
    date_trunc('hour', started_at, 'UTC'),
    campaign_id,
    count(*),
    count(*) FILTER (WHERE status = 'missed'),
    count(*) FILTER (WHERE status = 'connected'),
    count(*) FILTER (WHERE status = 'converted'),
    sum(duration_seconds)
FROM calls
WHERE account_id = :account_id AND started_at >= :start AND started_at < :end
GROUP BY 1, 2, 3
ON CONFLICT (account_id, bucket, campaign_id) DO UPDATE SET
    total = call_stats_hourly.total + EXCLUDED.total,
    missed = call_stats_hourly.missed + EXCLUDED.missed,
    connected = call_stats_hourly.connected + EXCLUDED.connected,
    converted = call_stats_hourly.converted + EXCLUDED.converted,
    duration_seconds = call_stats_hourly.duration_seconds + EXCLUDED.duration_seconds
