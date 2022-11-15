-- vim: set filetype=sql:
CREATE TABLE t1(a,b,c);
  INSERT INTO t1(a,b,c)
    VALUES(1,2,3),(7,8,9),(4,5,6),(10,11,12),(4,8,12),(1,11,111);
  CREATE INDEX t1a ON t1(a);
  CREATE INDEX t1b ON t1(b);
  ANALYZE;
  DELETE FROM sqlite_stat1;
  INSERT INTO sqlite_stat1(tbl,idx,stat)
    VALUES('t1','t1a','12345 2'),('t1','t1b','12345 4');
  ANALYZE sqlite_master;
  SELECT *, '#' FROM t1 WHERE a BETWEEN 3 AND 8 ORDER BY c;

EXPLAIN QUERY PLAN SELECT *, '#' FROM t1 WHERE a BETWEEN 3 AND 8 ORDER BY c;
SELECT c FROM t1 ORDER BY a;

EXPLAIN QUERY PLAN
  SELECT c FROM t1 ORDER BY a;

UPDATE sqlite_stat1 SET stat='12345 2 unordered' WHERE idx='t1a';
  ANALYZE sqlite_master;
  SELECT *, '#' FROM t1 WHERE a BETWEEN 3 AND 8 ORDER BY c;

EXPLAIN QUERY PLAN
  SELECT c FROM t1 ORDER BY a;
