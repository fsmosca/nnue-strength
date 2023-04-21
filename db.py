from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select


class Analysis(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    epd: str
    move: str
    score: int
    depth: Optional[int] = None
    engname: Optional[str] = None


sqlite_file_name = "positions.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)  # echo for debugging


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def is_exist(pos):
    with Session(engine) as session:
        epd = pos.epd
        move = pos.move

        statement = select(Analysis).where(Analysis.epd == epd).where(Analysis.move == move)
        results = session.exec(statement)
        return True if len(results.all()) else False


def insert_or_ignore(pos):
    with Session(engine) as session:
        epd = pos.epd
        move = pos.move

        statement = select(Analysis).where(Analysis.epd == epd).where(Analysis.move == move)
        results = session.exec(statement)
        ana = results.all()

        # Insert if not found.
        if len(ana) <= 0:
            session.add(pos)
            session.commit()


def create_pos():
    pos_1 = Analysis(epd="r1bqkbnr/pp3ppp/2n1p3/2ppP3/3P4/2P2N2/PP3PPP/RNBQKB1R b KQkq -", move="d8b6", score=-25)
    pos_2 = Analysis(epd="rnbqkb1r/pp1ppp1p/5np1/8/2PP4/2N5/PP3PPP/R1BQKBNR b KQkq -", move="d7d5", score=-17)

    with Session(engine) as session:
        session.add(pos_1)
        session.add(pos_2)
        session.commit()


def select_all_analysis():
    with Session(engine) as session:
        statement = select(Analysis)
        results = session.exec(statement)
        analysis = results.all()
        return analysis


def filter_analysis():
    with Session(engine) as session:
        statement = select(Analysis).where(Analysis.epd == "r1bqkbnr/pp3ppp/2n1p3/2ppP3/3P4/2P2N2/PP3PPP/RNBQKB1R b KQkq -").where(Analysis.move == "d8b6")
        results = session.exec(statement)
        ana = results.all()
        print(ana)
        # for r in ana:
            # print(r.epd)


def main():
    create_db_and_tables()
    create_pos()

    # filter_analysis()

    pos = Analysis(epd="rnbq1rk1/pp3ppp/4pn2/2pp4/1bPP4/2NBPN2/PP3PPP/R1BQK2R w KQ -", move="e1g1", score=25)
    insert_or_ignore(pos)

    pos = select_all_analysis()
    print(pos)


if __name__ == "__main__":
    main()
