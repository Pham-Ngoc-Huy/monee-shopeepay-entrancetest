-- Case study raw data: 500 users, 9,935 orders, 181 days, 2024-05-23 .. 2024-11-19.
-- Thresholds below are calibrated to this dataset (see notes at bottom).

WITH user_stats AS (
    SELECT
        user_id,
        COUNT(DISTINCT order_id)                           AS orders,
        SUM(net_merchant_value)                            AS nmv,
        SUM(net_merchant_value) / COUNT(DISTINCT order_id) AS avg_basket,
        100.0 * SUM(platform_discount + seller_discount)
              / SUM(gross_merchant_value)                   AS discount_pct,
        SUM(payment_method = 'BNPL')                       AS bnpl_orders,
        SUM(payment_method = 'Wallet')                     AS wallet_orders,
        julianday(MAX(create_date))                        AS last_order
    FROM orders
    GROUP BY user_id
),
segmented AS (
    SELECT
        user_id, orders, nmv, avg_basket, discount_pct, bnpl_orders, wallet_orders,
        last_order,
        NTILE(10) OVER (ORDER BY nmv DESC)                 AS value_decile,
        MAX(last_order) OVER ()                            AS as_of
    FROM user_stats
)
SELECT
    user_id, orders, ROUND(nmv, 2) AS nmv, ROUND(avg_basket, 2) AS avg_basket,
    ROUND(discount_pct, 2) AS discount_pct,
    ROUND(as_of - last_order) AS days_since_last,

    CASE WHEN orders = 1  THEN 'new_user'  ELSE 'repeat_buyer' END AS seg_frequency,
    CASE WHEN value_decile = 1               THEN 'high_value_user'       END AS seg_value,
    CASE WHEN bnpl_orders >= orders * 0.5   THEN 'BNPL_user'             END AS seg_bnpl,
    CASE WHEN wallet_orders >= orders * 0.5 THEN 'wallet_user'           END AS seg_wallet,
    CASE WHEN discount_pct >= 10            THEN 'discount_sensitive_user' END AS seg_discount,
    CASE WHEN as_of - last_order >= 30      THEN 'dormant_user'          END AS seg_dormant
FROM segmented
ORDER BY nmv DESC
LIMIT 10;


-- Population per segment. Segments overlap, so these sum to more than 500.
WITH user_stats AS (
    SELECT
        user_id,
        COUNT(DISTINCT order_id)                   AS orders,
        SUM(net_merchant_value)                    AS nmv,
        100.0 * SUM(platform_discount + seller_discount)
              / SUM(gross_merchant_value)          AS discount_pct,
        SUM(payment_method = 'BNPL')               AS bnpl_orders,
        SUM(payment_method = 'Wallet')             AS wallet_orders,
        julianday(MAX(create_date))                AS last_order
    FROM orders
    GROUP BY user_id
),
flags AS (
    SELECT
        CASE WHEN orders = 1 THEN 1 ELSE 0 END                    AS new_user,
        CASE WHEN orders >= 2 THEN 1 ELSE 0 END                   AS repeat_buyer,
        CASE WHEN NTILE(10) OVER (ORDER BY nmv DESC) = 1 THEN 1 ELSE 0 END AS high_value_user,
        CASE WHEN bnpl_orders >= orders * 0.5 THEN 1 ELSE 0 END   AS bnpl_user,
        CASE WHEN wallet_orders >= orders * 0.5 THEN 1 ELSE 0 END AS wallet_user,
        CASE WHEN discount_pct >= 10 THEN 1 ELSE 0 END            AS discount_sensitive,
        CASE WHEN MAX(last_order) OVER () - last_order >= 30
             THEN 1 ELSE 0 END                                    AS dormant_user
    FROM user_stats
)
SELECT 'new_user' AS segment, SUM(new_user) AS users FROM flags
UNION ALL SELECT 'repeat_buyer',       SUM(repeat_buyer)       FROM flags
UNION ALL SELECT 'high_value_user',    SUM(high_value_user)    FROM flags
UNION ALL SELECT 'BNPL_user',          SUM(bnpl_user)          FROM flags
UNION ALL SELECT 'wallet_user',        SUM(wallet_user)        FROM flags
UNION ALL SELECT 'discount_sensitive', SUM(discount_sensitive) FROM flags
UNION ALL SELECT 'dormant_user',       SUM(dormant_user)       FROM flags
ORDER BY users DESC;


-- Business summary: order and value mix by category x payment method.
SELECT
    category,
    payment_method,
    COUNT(*)                                  AS orders,
    ROUND(SUM(gross_merchant_value), 2)       AS gmv,
    ROUND(SUM(net_merchant_value), 2)         AS nmv,
    ROUND(100.0 * SUM(platform_discount) / SUM(gross_merchant_value), 2) AS platform_disc_pct,
    ROUND(AVG(net_merchant_value), 2)         AS avg_basket
FROM orders
GROUP BY category, payment_method
ORDER BY category, gmv DESC;

-- Threshold notes:
--   repeat_buyer        orders >= 2        -> 428 of 500 (72 users bought once)
--   high_value_user     nmv top decile     -> 50 users
--   BNPL / wallet_user  >= 50% of orders   -> 63 / 52 users
--                         (100%-of-orders is too tight: only 18 users each)
--   discount_sensitive  discount_pct >= 10 -> 263 users
--                         (avg is 15.6, so 10 keeps it a broad majority flag)
--   dormant_user        >= 30 days since last order
--   2 users have discount_pct > 100 (discount exceeds GMV) - quirk in the source data.
