-- vim: set filetype=sql:
PRAGMA auto_vacuum = 0;
  PRAGMA page_size = 1024;
  PRAGMA cache_size = 100;
  CREATE TABLE t1(a);

BEGIN;
      WITH s(i) AS (
        SELECT 1 UNION ALL SELECT i+1 FROM s WHERE i<200
      ) INSERT INTO t1 SELECT randomblob(900) FROM s;
