-- vim: set filetype=sql:
PRAGMA automatic_index = 0;
  CREATE TABLE t1(a, b);
  CREATE TABLE t2(c, d);
  CREATE TABLE t3(e, f);

EXPLAIN SELECT * FROM t1 WHERE a=1;
EXPLAIN SELECT * FROM t1 LEFT JOIN t2 ON (a=c AND a=10) WHERE d IS NULL;
EXPLAIN SELECT * FROM t1 LEFT JOIN t2 ON (a=c AND d=e) LEFT JOIN t3 ON (d=f);

