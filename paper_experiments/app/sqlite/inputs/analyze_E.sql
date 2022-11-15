-- vim: set filetype=sql:
CREATE TABLE t1(a,b);
WITH RECURSIVE cnt(x) AS (VALUES(1000) UNION ALL SELECT x+1 FROM cnt WHERE x<2000)
  INSERT INTO t1(a,b) SELECT x, x FROM cnt;
CREATE INDEX t1a ON t1(a);
ANALYZE;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a BETWEEN 500 AND 2500;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a BETWEEN 2900 AND 3000;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a BETWEEN 1700 AND 1750;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a BETWEEN 1 AND 500;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a BETWEEN 3000 AND 3000000;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a<500;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a>1100;


DROP TABLE t1;
  CREATE TABLE t1(a,b,c);
  WITH RECURSIVE
    cnt(x) AS (VALUES(1000) UNION ALL SELECT x+1 FROM cnt WHERE x<2000)
  INSERT INTO t1(a,b,c) SELECT x, x, 123 FROM cnt;
  CREATE INDEX t1ca ON t1(c,a);
  ANALYZE;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a BETWEEN 500 AND 2500 AND c=123;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a BETWEEN 1700 AND 1750 AND c=123;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a<500 AND c=123;

EXPLAIN QUERY PLAN
  SELECT * FROM t1 WHERE a<1900 AND c=123;
