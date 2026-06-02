import pyparsing as pp

word = pp.Word(pp.srange(r"[_,?'A-Z]"))

# phrase = pp.Opt(pp.Literal("/")) + pp.DelimitedList(expr=word, delim="/")

# l = phrase.parse_string("/ _  _ / _  _  _,/ _  _,/ _  _  _  _  _  _  _,/ _  _ / _  _  _  _  S  _,/ _  _ / _  _ / _  _  _  _ / _  _  _ / _  _  _ / _  _  _  _  _  _  _,/ _  _'_  _ / _  _  _  _  _  _  _  _ / _  _  _ / _  _  _  _  _  _?/")

words = pp.Opt(pp.Literal("/")).suppress() + \
    pp.DelimitedList(expr=word, delim="/").set_results_name("words", list_all_matches=True)

s = "/_  _ / _  _  _,/ _  _,/ _  _  _  _  _  _  _,/ _  _ / _  _  _  _  S  _,/ _  _ / _  _ / _  _  _  _ / _  _  _ / _  _  _ / _  _  _  _  _  _  _,/ _  _'_  _ / _  _  _  _  _  _  _  _ / _  _  _ / _  _  _  _  _  _?/".replace(" ", "")

l = words.parse_string(s, allow_trailing_delim=True)
