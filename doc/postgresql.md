Postgresql Helpful Tidbits
==========================

    SELECT max(id) from rssi_readings;

    ALTER SEQUENCE public.rssi_readings_id_seq RESTART WITH <value>;


    SELECT max(id) from training_runs;

    ALTER SEQUENCE public.training_runs_id_seq RESTART WITH <value>;


