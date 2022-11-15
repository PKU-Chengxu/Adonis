-- vim: set filetype=sql:
PRAGMA auto_vacuum=OFF;
    CREATE TABLE abc(a, b, c);
    INSERT INTO abc VALUES(1, 2, 3);

SELECT * FROM abc;

PRAGMA auto_vacuum=OFF;
  PRAGMA journal_mode=DELETE;
  CREATE TABLE t1(a, b);
  CREATE TABLE t2(c, d);
  INSERT INTO t1 VALUES('x', 'y');
  INSERT INTO t2 VALUES('i', 'j');

SELECT * FROM t1 UNION SELECT * FROM t2;
