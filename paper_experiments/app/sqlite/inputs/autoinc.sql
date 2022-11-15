-- vim: set filetype=sql:
SELECT name FROM sqlite_master WHERE type='table';

CREATE TABLE t1(x INTEGER PRIMARY KEY AUTOINCREMENT, y);
SELECT * FROM sqlite_sequence;
CREATE INDEX seqidx ON sqlite_sequence(name);

INSERT INTO t1 VALUES(1,23);
SELECT * FROM sqlite_sequence;

INSERT INTO t1 VALUES(123,456);
SELECT * FROM sqlite_sequence;

INSERT INTO t1 VALUES(NULL,567);
SELECT * FROM sqlite_sequence;

DELETE FROM t1 WHERE y=567;
SELECT * FROM sqlite_sequence;
