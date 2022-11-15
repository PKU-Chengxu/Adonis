-- vim: set filetype=sql:
CREATE TABLE t1(a, b);

INSERT INTO t1 VALUES(1, 2);
      INSERT INTO t1 VALUES(3, 4);
      SELECT count(*) FROM t1;


INSERT INTO t1 SELECT * FROM t1;          --   4
      INSERT INTO t1 SELECT * FROM t1;          --   8
      INSERT INTO t1 SELECT * FROM t1;          --  16
      INSERT INTO t1 SELECT * FROM t1;          --  32
      INSERT INTO t1 SELECT * FROM t1;          --  64
      INSERT INTO t1 SELECT * FROM t1;          -- 128
      INSERT INTO t1 SELECT * FROM t1;          -- 256
      SELECT count(*) FROM t1;

INSERT INTO t1 SELECT * FROM t1;          --  512
      INSERT INTO t1 SELECT * FROM t1;          -- 1024
      INSERT INTO t1 SELECT * FROM t1;          -- 2048
      INSERT INTO t1 SELECT * FROM t1;          -- 4096
      SELECT count(*) FROM t1;

CREATE TABLE t2(a, b);

SELECT count(*) FROM t2;
SELECT count(DISTINCT *) FROM t2;
SELECT count(DISTINCT a) FROM t2;
SELECT count(DISTINCT) FROM t2;
SELECT count(*) FROM t2 WHERE a IS NOT NULL;


CREATE TABLE t7(a INT,b TEXT,c BLOB,d REAL);
  CREATE TABLE t8(a INT,b TEXT,c BLOB,d REAL);
  CREATE INDEX t8a ON t8(a);

SELECT * FROM t8 WHERE (a, b) IN (
      SELECT count(t8.b), count(*) FROM t7 AS ra0 ORDER BY count(*)
  ) AND t8.b=0; 
