-- Input: the normalized permit table created by build_data.py.
-- Scope: Renton's published active permit-parcel snapshot, deduplicated by permit ID.
SELECT status, COUNT(*) AS permit_count
FROM permits
GROUP BY status
ORDER BY permit_count DESC;

-- Keep missing dates separate; do not infer that issued = finalized.
SELECT type,
       COUNT(*) AS total_permits,
       COUNT(issued) AS with_issue_date,
       COUNT(days_to_issue) AS with_valid_issue_interval,
       ROUND(AVG(days_to_issue), 1) AS mean_calendar_days_to_issue
FROM permits
GROUP BY type;

-- Application cohorts within an active-only snapshot are NOT historical demand.
SELECT SUBSTR(applied, 1, 7) AS application_month, COUNT(*) AS active_snapshot_records
FROM permits
WHERE applied IS NOT NULL
GROUP BY application_month
ORDER BY application_month;
