-- vim: set filetype=sql:
CREATE TABLE t1(
      a INTEGER PRIMARY KEY,
      b INTEGER
           REFERENCES t1 ON DELETE CASCADE
           REFERENCES t2,
      c TEXT,
      FOREIGN KEY (b,c) REFERENCES t2(x,y) ON UPDATE CASCADE
    );


CREATE TABLE t2(
      x INTEGER PRIMARY KEY,
      y TEXT
    );


CREATE TABLE t3(
      a INTEGER REFERENCES t2,
      b INTEGER REFERENCES t1,
      FOREIGN KEY (a,b) REFERENCES t2(x,y)
    );


CREATE TABLE t4(a integer primary key);
    CREATE TABLE t5(x references t4);
    CREATE TABLE t6(x references t4);
    CREATE TABLE t7(x references t4);
    CREATE TABLE t8(x references t4);
    CREATE TABLE t9(x references t4);
    CREATE TABLE t10(x references t4);
    DROP TABLE t7;
    DROP TABLE t9;
    DROP TABLE t5;
    DROP TABLE t8;
    DROP TABLE t6;
    DROP TABLE t10;

CREATE TABLE t5(a PRIMARY KEY, b, c);
    CREATE TABLE t6(
      d REFERENCES t5,
      e REFERENCES t5(c)
    );
    PRAGMA foreign_key_list(t6);

CREATE TABLE t7(d, e, f,
      FOREIGN KEY (d, e) REFERENCES t5(a, b)
    );
    PRAGMA foreign_key_list(t7);

CREATE TABLE t8(d, e, f,
      FOREIGN KEY (d, e) REFERENCES t5 ON DELETE CASCADE ON UPDATE SET NULL
    );
    PRAGMA foreign_key_list(t8);

CREATE TABLE t9(d, e, f,
      FOREIGN KEY (d, e) REFERENCES t5 ON DELETE CASCADE ON UPDATE SET DEFAULT
    );
    PRAGMA foreign_key_list(t9);

PRAGMA foreign_keys=ON;
  CREATE TABLE "xx1"("xx2" TEXT PRIMARY KEY, "xx3" TEXT);
  INSERT INTO "xx1"("xx2","xx3") VALUES('abc','def');
  CREATE TABLE "xx4"("xx5" TEXT REFERENCES "xx1" ON DELETE CASCADE);
  INSERT INTO "xx4"("xx5") VALUES('abc');
  INSERT INTO "xx1"("xx2","xx3") VALUES('uvw','xyz');
  SELECT 1, "xx5" FROM "xx4";
  DELETE FROM "xx1";
  SELECT 2, "xx5" FROM "xx4";

