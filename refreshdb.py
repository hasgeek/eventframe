#!/usr/bin/env python
# Adapted from https://zignar.net/2011/11/01/copy-data-from-mysql-to-postgres-using-sqlalchemy/

from sqlalchemy import create_engine
import eventframe
from eventframe.models import db


def refresh(base, srcdb, dstdb):
    src = create_engine(srcdb)
    dst = create_engine(dstdb)

    tables = base.metadata.tables
    for tbl in tables:
        print ('##################################')
        print (tbl)
        print (tables[tbl].select())
        data = src.execute(tables[tbl].select()).fetchall()
        for a in data:
            print(a)
        if data:
            print (tables[tbl].insert())
            dst.execute(tables[tbl].insert(), data)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print >> sys.stderr, "Syntax: %s source-db destination-db" % sys.argv[0]
        print >> sys.stderr, "Example: %s sqlite:///old.db sqlite:///new.db" % sys.argv[0]
    else:
        eventframe.init_for('dev')
        refresh(db.Model, sys.argv[1], sys.argv[2])
