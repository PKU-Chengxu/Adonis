-- vim: set filetype=sql:
CREATE TABLE t1(x, y);
  BEGIN;
    INSERT INTO t1 VALUES(1, 2);

COMMIT;
