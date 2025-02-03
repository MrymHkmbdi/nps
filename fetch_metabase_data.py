import requests
import pandas as pd

username = "m.hokmabadi@bimebazar.com"
password = "CEme12031399"

sql_query = """
    WITH paid_orders AS (
    SELECT 
        DATE(o.first_paid_date) AS paid_date_day,
        SUM(o.price) AS total_nmv,
        SUM(CASE WHEN o.type = 'carbody' THEN o.price ELSE 0 END) AS carbody_nmv,
        SUM(CASE WHEN o.type = 'thirdparty' THEN o.price ELSE 0 END) AS thirdparty_nmv,
        SUM(CASE WHEN o.type NOT IN ('carbody', 'thirdparty') THEN o.price ELSE 0 END) AS other_types_nmv,
        SUM(CASE WHEN o.partner_id = 51 THEN o.price ELSE 0 END) AS sellers_nmv,
        SUM(CASE WHEN o.partner_id = 29 THEN o.price ELSE 0 END) AS snappbimeh_nmv,
        SUM(CASE 
            WHEN (pap.white_label = FALSE OR pap.white_label IS NULL) 
                THEN o.price 
                ELSE 0 
            END) AS bimebazar_nmv,
        -- SUM(CASE WHEN (o.partner_id IN (30, 48, 49, 43, 45, 52, 53, 54, 27, 9, 44, 18, 8, 10, 2, 40, 7, 5, 33, 45,49,48,53,52,43,54,57,58,60,59) OR o.partner_id IS NULL) THEN o.price ELSE 0 END) AS bimebazar_nmv,
        SUM(CASE  WHEN (pap.white_label = FALSE OR pap.white_label IS NULL) THEN o.price ELSE 0 END) AS other_partners_nmv,
        SUM(EXTRACT(EPOCH FROM (o.issued_date - o.first_paid_date))) / 3600 AS total_issuance_time_hours,
        SUM(CASE 
            WHEN o.issued_date <= o.first_paid_date + INTERVAL '20 Minutes' 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL)
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1
        END) AS bb_twenty_minutes_sla_count,

        SUM(CASE 
            WHEN o.issued_date <= o.first_paid_date + INTERVAL '2 Hours' 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL)
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1
        END) AS bb_two_hours_sla_count,

        SUM(CASE 
            WHEN EXTRACT(HOUR FROM o.first_paid_date) < 21 
            AND DATE(o.issued_date) = DATE(o.first_paid_date) 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL)
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1
        END) AS bb_redline_sla_counts,
         SUM(CASE 
            WHEN EXTRACT(HOUR FROM o.first_paid_date) < 21 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL)
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1
        END) AS bb_before_9_thirdparty_count,

        SUM(CASE 
            WHEN o.issued_date <= o.first_paid_date + INTERVAL '20 Minutes' 
            AND o.partner_id = 29 
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1
        END) AS sb_twenty_minutes_sla_count,

        SUM(CASE 
            WHEN o.issued_date <= o.first_paid_date + INTERVAL '2 Hours'
            AND o.partner_id = 29 
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1
        END) AS sb_two_hours_sla_count,

        SUM(CASE 
            WHEN EXTRACT(HOUR FROM o.first_paid_date) < 21 
            AND DATE(o.issued_date) = DATE(o.first_paid_date) 
            AND o.partner_id = 29 
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1
        END) AS sb_redline_sla_counts,
        SUM(CASE 
            WHEN EXTRACT(HOUR FROM o.first_paid_date) < 21 
            AND (o.partner_id = 29)
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1
        END) AS sb_before_9_thirdparty_count,

        COUNT(*) AS count_of_orders,
        SUM(CASE 
             WHEN (pap.white_label = FALSE OR pap.white_label IS NULL) AND installment_type='cash' THEN 1 ELSE 0
        END) AS bb_count_of_cash_orders,
        SUM(CASE 
            WHEN o.type = 'carbody' 
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            THEN 1 ELSE 0
        END) AS total_carbody_count,
        SUM(CASE 
            WHEN o.type = 'thirdparty' THEN 1 ELSE 0
        END) AS total_thirdparty_count,
        SUM(CASE 
            WHEN o.issued_date <= o.first_paid_date + INTERVAL '48 Hours'
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'carbody' THEN 1
        END) AS carbody_48hours,
        SUM(CASE 
            WHEN (pap.white_label = FALSE OR pap.white_label IS NULL)
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1 ELSE 0
        END) AS thirdparty_bb_order_count,

        SUM(CASE 
            WHEN o.partner_id = 29 
            AND o.id NOT IN (
                            SELECT DISTINCT order_id
                            FROM order_orderstatelog
                            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
                            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
                            WHERE order_state.id IN (36,21))
            AND o.type = 'thirdparty' THEN 1 ELSE 0 
        END) AS thirdparty_snappbimeh_order_count,

        SUM(CASE 
            WHEN o.company_id IN (19, 29, 36) 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL) THEN o.price ELSE 0 
        END) AS bb_league1_nmv,

        SUM(CASE 
            WHEN o.company_id IN (2, 5, 6, 21) 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL) THEN o.price ELSE 0 
        END) AS bb_league2_nmv,

        SUM(CASE 
            WHEN o.company_id NOT IN (2, 5, 6, 19, 21, 29, 36) 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL) THEN o.price ELSE 0 
        END) AS bb_other_league_nmv,

        SUM(CASE 
            WHEN o.company_id IN (19, 29, 36) 
            AND o.partner_id = 29 THEN o.price ELSE 0 
        END) AS snappbimeh_league1_nmv,

        SUM(CASE 
            WHEN o.company_id IN (2, 5, 6, 21) 
            AND o.partner_id = 29 THEN o.price ELSE 0 
        END) AS snappbimeh_league2_nmv,

        SUM(CASE 
            WHEN o.company_id NOT IN (2, 5, 6, 19, 21, 29, 36) 
            AND o.partner_id = 29 THEN o.price ELSE 0 
        END) AS snappbimeh_other_league_nmv,

        SUM(CASE 
            WHEN o.installment_type = 'bb_bnpl' 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL) THEN o.price ELSE 0 
        END) AS bb_bnpl_nmv,

        SUM(CASE 
            WHEN o.installment_type = 'cash' 
            AND (pap.white_label = FALSE OR pap.white_label IS NULL) THEN o.price ELSE 0 
        END) AS bb_cash_nmv,

        SUM(CASE 
            WHEN o.installment_type = 'bb_bnpl' 
            AND o.partner_id = 29 THEN o.price ELSE 0 
        END) AS snappbime_bnpl_nmv,

        SUM(CASE 
            WHEN o.installment_type = 'cash' 
            AND o.partner_id = 29 THEN o.price ELSE 0 
        END) AS snappbime_cash_nmv,

        SUM(CASE 
             WHEN (pap.white_label = FALSE OR pap.white_label IS NULL) AND o.installment_type = 'cash' THEN COALESCE(c.voucher_amount, 0) ELSE 0 
        END) AS bb_voucher_amount,

        SUM(CASE 
             WHEN (pap.white_label = FALSE OR pap.white_label IS NULL)
            AND COALESCE(c.voucher_amount, 0) = 0 
             AND o.installment_type = 'cash' THEN 1 ELSE 0 
        END) AS bb_non_voucher_count
    FROM 
        order_order o
    LEFT JOIN 
        insurance_insurancecompany cn ON o.partner_id = cn.id
    LEFT JOIN 
        partners_api_partner pap ON pap.id = o.partner_id
    LEFT JOIN (
        SELECT
            oi.order_id,
            SUM(CASE WHEN pc.type = 'voucher' THEN ocp.amount ELSE 0 END) AS voucher_amount
        FROM order_payment_invoice oi
        LEFT JOIN order_payment_creditorderpayment ocp ON oi.id = ocp.invoice_id
        LEFT JOIN promotion_credit pc ON ocp.credit_id = pc.id
        WHERE oi.invoice_type = 'main'
        GROUP BY oi.order_id
    ) c ON o.id = c.order_id
    WHERE 
        o.first_paid_date IS NOT NULL 
        AND o.state_id NOT IN (1, 2, 3, 5, 38)
        AND o.id NOT IN (
            SELECT DISTINCT order_id
            FROM order_orderstatelog
            LEFT JOIN order_transition ON order_orderstatelog.transition_id = order_transition.id
            LEFT JOIN order_state ON order_state.id = order_transition.to_state_id
            WHERE order_state.id = 36
        )
    GROUP BY 
        paid_date_day
),
created_orders AS (
    SELECT 
        created_date::DATE AS created_date,
        COUNT(*) AS count_of_created_orders,
        COUNT(*) FILTER (WHERE o.type = 'thirdparty') AS created_thirdparty_orders,
        COUNT(*) FILTER (WHERE o.type = 'carbody') AS created_carbody_orders
    FROM 
        order_order o
    WHERE 
        state_id = 1
    GROUP BY 
        created_date::DATE
),
user_cancelled AS (
    SELECT 
        first_paid_date::DATE, 
        type, 
        COUNT(*) AS counter
    FROM 
        public.order_order
    WHERE 
        state_id IN (0, 1, 5) 
        AND first_paid_date IS NOT NULL 
    GROUP BY 
        first_paid_date::DATE, 
        type
),
user_cancelled_orders AS (
    SELECT 
        first_paid_date::DATE AS created_date,
        SUM(CASE 
                WHEN type = 'thirdparty' THEN counter ELSE 0
            END) AS thirdparty_cancelled_count,
        SUM(CASE 
                WHEN type = 'carbody' THEN counter ELSE 0 
            END) AS carbody_cancelled_count
    FROM 
        user_cancelled
    GROUP BY 
        first_paid_date::DATE
)
SELECT 
    (p.paid_date_day - INTERVAL '1 year')::DATE As last_year_today,
    p.*, 
    c.count_of_created_orders, c.created_carbody_orders, c.created_thirdparty_orders, 
    u.thirdparty_cancelled_count, u.carbody_cancelled_count 
FROM 
    paid_orders p
LEFT JOIN 
    created_orders c ON c.created_date = p.paid_date_day
LEFT JOIN 
    user_cancelled_orders u ON u.created_date = p.paid_date_day
ORDER BY 
    p.paid_date_day DESC;
"""


def fetch_metabase_data():
    response = requests.post(
        "https://bijik.bimebazar.com/api/session",
        json={"username": "m.hokmabadi@bimebazar.com", "password": "CEme12031399"}
    )
    if response.status_code != 200:
        raise Exception(f"Failed to log in to Metabase: {response.text}")
    token = response.json()["id"]

    # Run SQL query
    headers = {"X-Metabase-Session": token}
    payload = {
        "type": "native",
        # "native": {"query": sql_query.format(start_date=start_date, end_date=end_date)},
        "native": {"query": sql_query},
        "database": 2
    }
    response = requests.post(
        "https://bijik.bimebazar.com/api/dataset",
        headers=headers,
        json=payload
    )
    if not response.ok:
        raise Exception(f"Failed to run SQL query: {response.text}")

    # Convert results to DataFrame
    rows = response.json().get("data", {}).get("rows", [])
    cols = [col["display_name"] for col in response.json().get("data", {}).get("cols", [])]
    df = pd.DataFrame(rows, columns=cols)

    return df
