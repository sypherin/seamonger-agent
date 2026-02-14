from src.parser import parse_stock_signal


def test_parse_singlish_malay_stock_signal():
    signal = parse_stock_signal("aku ada 50kg bawal")

    assert signal.product == "bawal"
    assert signal.quantity_kg == 50.0
    assert signal.confidence >= 0.8
