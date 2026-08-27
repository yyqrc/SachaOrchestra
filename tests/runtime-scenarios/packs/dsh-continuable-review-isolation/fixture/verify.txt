from token_mask import mask_token

cases = {
    "": "",
    "a": "*",
    "abcd": "****",
    "abcde": "*bcde",
    "123456789": "*****6789",
}

for value, expected in cases.items():
    actual = mask_token(value)
    assert actual == expected, (value, expected, actual)

print("verification=pass cases=5")
