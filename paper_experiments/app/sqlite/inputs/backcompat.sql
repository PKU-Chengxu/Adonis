-- vim: set filetype=sql:

CREATE TABLE t2(a UNIQUE, b PRIMARY KEY, c UNIQUE);
      INSERT INTO t2 VALUES(1,9,5);
      INSERT INTO t2 VALUES(5,5,1);
      INSERT INTO t2 VALUES(9,1,9);
      SELECT * FROM t2 ORDER BY a;

SELECT * FROM sqlite_master WHERE rootpage=-1;
      SELECT * FROM t2 ORDER BY a;

SELECT * FROM t2 ORDER BY b;
