-- vim: set filetype=sql:
PRAGMA auto_vacuum=OFF;
      PRAGMA page_size = 1024;
      CREATE TABLE t1(x);
      INSERT INTO t1 VALUES(1.1);

SELECT * FROM t1;
SELECT datetime(x) FROM t1;
