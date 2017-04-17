from kaeru_parser import add_numbers


class TestClass:
    def test_E(self):
        text = add_numbers('tests/E.txt')
        assert_text = open('tests/E_correct.txt').read()
        assert text == assert_text

    def test_F(self):
        text = add_numbers('tests/F.txt')
        assert_text = open('tests/F_correct.txt').read()
        assert text == assert_text

    def test_G(self):
        text = add_numbers('tests/G.txt')
        assert_text = open('tests/G_correct.txt').read()
        assert text == assert_text
