-- ============================================================
-- Snowflake Schema for CyberDemo SIEM Data
-- ============================================================
-- Run once to create database, schema, warehouse, and tables.
-- Usage: python scripts/setup_snowflake.py --schema-only
-- ============================================================

CREATE DATABASE IF NOT EXISTS CYBER_SECURITY;
USE DATABASE CYBER_SECURITY;

CREATE SCHEMA IF NOT EXISTS SIEM;
USE SCHEMA SIEM;

CREATE WAREHOUSE IF NOT EXISTS CYBER_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

USE WAREHOUSE CYBER_WH;

-- ML anomaly scores per host — one row per monitored entity
CREATE TABLE IF NOT EXISTS ANOMALY_SCORES (
    score_id        VARCHAR(20)  NOT NULL,
    entity_type     VARCHAR(10)  NOT NULL,       -- HOST, SERVICE, USER
    entity_name     VARCHAR(50)  NOT NULL,       -- hostname
    entity_ip       VARCHAR(15)  NOT NULL,
    current_score   FLOAT        NOT NULL,       -- 0-10 threat score
    baseline_score  FLOAT        NOT NULL,
    anomaly_delta   FLOAT        NOT NULL,
    anomaly_label   VARCHAR(30)  NOT NULL,       -- CRITICAL_ANOMALY, HIGH_ANOMALY
    contributing_factors VARIANT  NOT NULL,       -- JSON with attack details
    model_version   VARCHAR(20)  NOT NULL,
    computed_at     TIMESTAMP_NTZ NOT NULL,
    PRIMARY KEY (score_id)
);

-- Endpoint detection events (EDR/XDR)
CREATE TABLE IF NOT EXISTS ENDPOINT_EVENTS (
    event_id        VARCHAR(20)  NOT NULL,
    hostname        VARCHAR(50)  NOT NULL,
    event_type      VARCHAR(30)  NOT NULL,       -- MALWARE, ENCRYPTION, OUTBOUND, etc.
    severity        VARCHAR(10)  NOT NULL,       -- CRITICAL, HIGH, MEDIUM, LOW
    detection_name  VARCHAR(80)  NOT NULL,
    risk_score      FLOAT        NOT NULL,
    process_name    VARCHAR(80),
    file_path       VARCHAR(200),
    event_time      TIMESTAMP_NTZ NOT NULL,
    PRIMARY KEY (event_id)
);

-- Network flow events (firewall/IDS)
CREATE TABLE IF NOT EXISTS NETWORK_EVENTS (
    event_id        VARCHAR(20)  NOT NULL,
    source_host     VARCHAR(50)  NOT NULL,
    source_ip       VARCHAR(15)  NOT NULL,
    dest_ip         VARCHAR(15)  NOT NULL,
    dest_port       INT          NOT NULL,
    protocol        VARCHAR(10)  NOT NULL,
    bytes_sent      BIGINT       NOT NULL,
    bytes_received  BIGINT       NOT NULL,
    geo_country     VARCHAR(5)   NOT NULL,       -- ISO country code
    event_time      TIMESTAMP_NTZ NOT NULL,
    PRIMARY KEY (event_id)
);
