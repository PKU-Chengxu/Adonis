-- vim: set filetype=sql:
CREATE TABLE t1(a,b,c,d);
  CREATE TABLE t2(x,y,z);
  INSERT INTO t1(a,b) VALUES(10, 15);
  INSERT INTO t1(a,b) VALUES(20, 25);
  INSERT INTO t2(x,y) VALUES('ten', 'fifteen');
  INSERT INTO t2(x,y) VALUES('twenty', 'twentyfive');
  CREATE TABLE t3(id TEXT PRIMARY KEY, a, b, c, d) WITHOUT ROWID;
  INSERT INTO t3(id,a,b,c,d) SELECT rowid, a, b, c, d FROM t1;
  PRAGMA automatic_index = 0;


SELECT * FROM t1 CROSS JOIN t2 WHERE a=x;
EXPLAIN SELECT * FROM t1 WHERE a=15 AND c=22 AND rowid!=98;

SELECT * FROM t1 WHERE b>11;

EXPLAIN SELECT c FROM t1 WHERE b>=10 AND b<=20 ORDER BY b ASC;
EXPLAIN SELECT rowid FROM t1 WHERE b=22 AND c>=10 AND c<=20 ORDER BY b,c DESC;

