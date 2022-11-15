-- vim: set filetype=sql:
CREATE TABLE t1(a, b);
  INSERT INTO t1 VALUES(1, 2);
  BEGIN;
    INSERT INTO t1 VALUES(3, 4);


COMMIT;
  CREATE TABLE t2(a, b);
  BEGIN;
    INSERT INTO t1 VALUES(5, 6);
    INSERT INTO t2 VALUES('a', 'b');

SELECT * FROM t1;
    SELECT * FROM t2;


COMMIT;
  CREATE TABLE t3(a, b);
  BEGIN;
    INSERT INTO t1 VALUES(7, 8);
    INSERT INTO t2 VALUES('c', 'd');
    INSERT INTO t3 VALUES('i', 'ii');


SELECT * FROM t1;
    SELECT * FROM t2;
    SELECT * FROM t3;
