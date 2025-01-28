from ninja import Schema


class ObsceneWordsOut(Schema):
    value: str
    calc_similarity: float
