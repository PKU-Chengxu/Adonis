-- vim: set filetype=sql:
CREATE TABLE t1(i INTEGER PRIMARY KEY,a,b,c,d);
    CREATE INDEX t1i1 ON t1(a DESC, b ASC, c DESC);
    CREATE INDEX t1i2 ON t1(b DESC, c ASC, d DESC);


INSERT INTO t1 VALUES(1, NULL, NULL, NULL, NULL);
    INSERT INTO t1 VALUES(2, 2, 2, 2, 2);
    INSERT INTO t1 VALUES(3, 3, 3, 3, 3);
    INSERT INTO t1 VALUES(4, 2.5, 2.5, 2.5, 2.5);
    INSERT INTO t1 VALUES(5, -5, -5, -5, -5);
    INSERT INTO t1 VALUES(6, 'six', 'six', 'six', 'six');
    INSERT INTO t1 VALUES(7, x'77', x'77', x'77', x'77');
    INSERT INTO t1 VALUES(8, 'eight', 'eight', 'eight', 'eight');
    INSERT INTO t1 VALUES(9, x'7979', x'7979', x'7979', x'7979');
    SELECT count(*) FROM t1;

SELECT i FROM t1 ORDER BY a;
SELECT i FROM t1 ORDER BY a DESC;

UPDATE t1 SET a=1;
    SELECT i FROM t1 ORDER BY a;

SELECT i FROM t1 WHERE a=1 AND b>-9999 AND b<x'ffffffff';

UPDATE t1 SET a=1;
      SELECT i FROM t1 WHERE a IN (1,2) AND b>0 AND b<'zzz';

